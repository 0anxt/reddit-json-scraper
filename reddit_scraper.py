#!/usr/bin/env python3
"""
Reddit JSON Scraper Bot
A comprehensive Reddit scraping tool using the public JSON API
No authentication required!
"""

import requests
import json
import os
import time
import random
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
from pathlib import Path
from datetime import datetime
from rag_formatter import save_text_post_rag
from chatbot_formatter import save_text_post_chatbot

# Rotating User-Agents to avoid blocks
_USER_AGENTS = [
    "RedditJSONScraper/1.0 (+https://github.com/0anxt/reddit-json-scraper)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class RedditJSONScraper:
    """Main scraper class for Reddit content using JSON API"""
    
    def __init__(self, output_dir: str = "reddit_downloads", user_agent: str = None, output_format: str = "classic"):
        """
        Initialize the Reddit scraper
        
        Args:
            output_dir: Directory to save downloaded content
            user_agent: Custom user agent string
            output_format: Output format - 'classic' or 'rag' (RAG-optimized)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.output_format = output_format  # 'classic' or 'rag'
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or _USER_AGENTS[0],
            "Accept": "application/json",
        })
        
        self.rate_limit_delay = 2  # seconds between requests
        self.last_request_time = 0
        self._ua_index = 0

    def _rotate_user_agent(self):
        """Rotate to a different User-Agent to avoid 403s"""
        self._ua_index = (self._ua_index + 1) % len(_USER_AGENTS)
        self.session.headers["User-Agent"] = _USER_AGENTS[self._ua_index]
    
    def _rate_limit(self):
        """Implement rate limiting to avoid IP bans"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _fetch_json(self, url: str, _retries: int = 0) -> Optional[Dict]:
        """
        Fetch JSON data from a URL with exponential-backoff retry on transient failures.
        
        Args:
            url: URL to fetch
            _retries: Internal retry counter (do not pass manually)
            
        Returns:
            Parsed JSON data or None on permanent failure after retries exhausted
        """
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=30)
            
            # 429 Rate limited — back off and retry
            if response.status_code == 429:
                if _retries >= 5:
                    print(f"⚠️  Rate limited after 5 retries. Giving up on: {url}")
                    return None
                wait = (2 ** _retries) + random.uniform(0, 1)  # exponential backoff + jitter
                print(f"⚠️  Rate limited. Waiting {wait:.1f}s (retry {_retries + 1}/5)...")
                time.sleep(wait)
                return self._fetch_json(url, _retries + 1)
            
            # 403 Forbidden — rotate UA and retry once
            if response.status_code == 403:
                if _retries >= 1:
                    print(f"❌ Access forbidden after retry: {url}")
                    return None
                print(f"⚠️  403 Forbidden — rotating User-Agent and retrying...")
                self._rotate_user_agent()
                return self._fetch_json(url, _retries + 1)
            
            # 5xx Server errors — treat as transient, retry with backoff
            if 500 <= response.status_code < 600:
                if _retries >= 5:
                    print(f"❌ Server error {response.status_code} after 5 retries. Giving up on: {url}")
                    return None
                wait = (2 ** _retries) + random.uniform(0, 1)
                print(f"⚠️  Server error {response.status_code}. Waiting {wait:.1f}s (retry {_retries + 1}/5)...")
                time.sleep(wait)
                return self._fetch_json(url, _retries + 1)
            
            # Any other non-OK status
            if response.status_code != 200:
                print(f"❌ Unexpected status {response.status_code} for {url}")
                return None
            
            return response.json()
            
        except requests.ConnectionError as e:
            if _retries >= 5:
                print(f"❌ Connection error after 5 retries: {e}")
                return None
            wait = (2 ** _retries) + random.uniform(0, 1)
            print(f"⚠️  Connection error. Waiting {wait:.1f}s (retry {_retries + 1}/5)...")
            time.sleep(wait)
            return self._fetch_json(url, _retries + 1)
            
        except requests.RequestException as e:
            print(f"❌ Request error for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove invalid characters
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\s+', '_', filename)
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def fetch_subreddit(self, subreddit: str, sort: str = "hot", 
                       time_filter: str = "day", limit: int = 100) -> List[Dict]:
        """
        Fetch posts from a subreddit
        
        Args:
            subreddit: Subreddit name (without r/)
            sort: Sort method (hot, new, top, rising, controversial)
            time_filter: Time filter for top/controversial (hour, day, week, month, year, all)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post data dictionaries
        """
        posts = []
        after = None
        
        print(f"📥 Fetching r/{subreddit} ({sort}, limit={limit})...")
        
        while len(posts) < limit:
            # Build URL
            if sort in ["top", "controversial"]:
                url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?t={time_filter}&limit=100"
            else:
                url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100"
            
            if after:
                url += f"&after={after}"
            
            data = self._fetch_json(url)
            if not data:
                break
            
            # Extract posts
            children = data.get('data', {}).get('children', [])
            if not children:
                break
            
            for child in children:
                if child['kind'] == 't3':  # t3 = post
                    posts.append(child['data'])
                    if len(posts) >= limit:
                        break
            
            # Get pagination token
            after = data.get('data', {}).get('after')
            if not after:
                break
        
        print(f"✓ Fetched {len(posts)} posts from r/{subreddit}")
        return posts
    
    def fetch_user(self, username: str, sort: str = "new", limit: int = 100) -> List[Dict]:
        """
        Fetch posts from a user
        
        Args:
            username: Username (without u/)
            sort: Sort method (hot, new, top, controversial)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post data dictionaries
        """
        posts = []
        after = None
        
        print(f"📥 Fetching u/{username} posts ({sort}, limit={limit})...")
        
        while len(posts) < limit:
            url = f"https://www.reddit.com/user/{username}/submitted.json?sort={sort}&limit=100"
            
            if after:
                url += f"&after={after}"
            
            data = self._fetch_json(url)
            if not data:
                break
            
            children = data.get('data', {}).get('children', [])
            if not children:
                break
            
            for child in children:
                if child['kind'] == 't3':
                    posts.append(child['data'])
                    if len(posts) >= limit:
                        break
            
            after = data.get('data', {}).get('after')
            if not after:
                break
        
        print(f"✓ Fetched {len(posts)} posts from u/{username}")
        return posts
    
    def fetch_post_with_comments(self, post_url: str) -> Optional[Tuple[Dict, List[Dict]]]:
        """
        Fetch a single post with its comments
        
        Args:
            post_url: Reddit post URL or permalink
            
        Returns:
            Tuple of (post_data, comments_list) or None
        """
        # Convert URL to JSON endpoint
        if not post_url.endswith('.json'):
            post_url = post_url.rstrip('/') + '.json'
        
        data = self._fetch_json(post_url)
        if not data or len(data) < 2:
            return None
        
        # Extract post and comments
        post_data = data[0]['data']['children'][0]['data']
        comments_data = data[1]['data']['children']
        
        # Parse comments recursively
        comments = self._parse_comments(comments_data)
        
        return post_data, comments
    
    def _parse_comments(self, comments_data: List[Dict], depth: int = 0, max_depth: int = 5) -> List[Dict]:
        """
        Recursively parse comment tree
        
        Args:
            comments_data: Raw comments data from API
            depth: Current nesting depth
            max_depth: Maximum depth to parse
            
        Returns:
            List of parsed comment dictionaries
        """
        comments = []
        
        for item in comments_data:
            if item['kind'] == 't1':  # t1 = comment
                comment_data = item['data']
                
                # Skip deleted/removed comments
                if comment_data.get('author') in ['[deleted]', '[removed]']:
                    continue
                
                comment = {
                    'author': comment_data.get('author', '[unknown]'),
                    'body': comment_data.get('body', ''),
                    'score': comment_data.get('score', 0),
                    'created_utc': comment_data.get('created_utc', 0),
                    'depth': depth,
                    'replies': []
                }
                
                # Parse nested replies
                if depth < max_depth and 'replies' in comment_data:
                    replies_data = comment_data['replies']
                    if isinstance(replies_data, dict):
                        reply_children = replies_data.get('data', {}).get('children', [])
                        comment['replies'] = self._parse_comments(reply_children, depth + 1, max_depth)
                
                comments.append(comment)
            
            elif item['kind'] == 'more':
                # Handle "load more comments" - skip for now
                continue
        
        return comments
    
    def download_media(self, url: str, save_path: Path) -> bool:
        """
        Download media file from URL
        
        Args:
            url: Media URL
            save_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            return False
    
    def save_text_post(self, post_data: Dict, comments: List[Dict], save_path: Path):
        """
        Save text/self post as markdown with comments
        
        Args:
            post_data: Post data dictionary
            comments: List of comment dictionaries
            save_path: Path to save the markdown file
        """
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.output_format == 'rag':
            self._save_text_post_rag(post_data, comments, save_path)
        elif self.output_format == 'chatbot':
            self._save_text_post_chatbot(post_data, comments, save_path)
        else:
            self._save_text_post_classic(post_data, comments, save_path)
    
    def _save_text_post_rag(self, post_data: Dict, comments: List[Dict], save_path: Path):
        """Save text post in RAG-optimized format"""
        save_text_post_rag(post_data, comments, save_path)
    
    def _save_text_post_chatbot(self, post_data: Dict, comments: List[Dict], save_path: Path):
        """Save text post in chatbot template format"""
        save_text_post_chatbot(post_data, comments, save_path)
    
    def _save_text_post_classic(self, post_data: Dict, comments: List[Dict], save_path: Path):
        """Save text post in classic format"""
        with open(save_path, 'w', encoding='utf-8') as f:
            # Write post header
            f.write(f"# {post_data['title']}\n\n")
            f.write(f"**Author:** u/{post_data['author']}\n\n")
            f.write(f"**Subreddit:** r/{post_data['subreddit']}\n\n")
            f.write(f"**Score:** {post_data['score']} upvotes\n\n")
            f.write(f"**Created:** {datetime.fromtimestamp(post_data['created_utc']).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**URL:** https://reddit.com{post_data['permalink']}\n\n")
            f.write("-" * 80 + "\n\n")
            
            # Write post body
            if post_data.get('selftext'):
                f.write("## Post Content\n\n")
                f.write(post_data['selftext'] + "\n\n")
                f.write("-" * 80 + "\n\n")
            
            # Write comments
            if comments:
                f.write(f"## Comments ({len(comments)})\n\n")
                self._write_comments(f, comments)
    
    def _write_comments(self, file, comments: List[Dict], indent: int = 0):
        """
        Recursively write comments to file
        
        Args:
            file: File object to write to
            comments: List of comment dictionaries
            indent: Current indentation level
        """
        for comment in comments:
            prefix = "  " * indent + "> " if indent > 0 else ""
            
            file.write(f"{prefix}**u/{comment['author']}** ({comment['score']} points):\n")
            file.write(f"{prefix}{comment['body']}\n\n")
            
            # Write nested replies
            if comment['replies']:
                self._write_comments(file, comment['replies'], indent + 1)
    
    def save_link_post(self, post_data: Dict, save_path: Path):
        """
        Save link post as HTML redirect
        
        Args:
            post_data: Post data dictionary
            save_path: Path to save the HTML file
        """
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = f"""<html>
<head>
    <title>{post_data['title']}</title>
    <meta http-equiv="refresh" content="0; url={post_data['url']}" />
</head>
<body>
    <h1>{post_data['title']}</h1>
    <p>Redirecting to: <a href="{post_data['url']}">{post_data['url']}</a></p>
    <script type='text/javascript'>
        window.location.href = "{post_data['url']}";
    </script>
</body>
</html>"""
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def download_post(self, post_data: Dict, target_dir: Path, include_comments: bool = True) -> bool:
        """
        Download a single post with appropriate handler based on type
        
        Args:
            post_data: Post data dictionary
            target_dir: Directory to save the post
            include_comments: Whether to fetch and save comments
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create safe filename
            post_id = post_data['id']
            title = self._sanitize_filename(post_data['title'])
            author = post_data['author']
            
            # Determine post type and handle accordingly
            if post_data.get('is_self'):
                # Text/self post
                filename = f"{post_id}_{title}.md"
                save_path = target_dir / filename
                
                if include_comments:
                    # Fetch comments
                    permalink = post_data['permalink']
                    url = f"https://www.reddit.com{permalink}.json"
                    result = self.fetch_post_with_comments(url)
                    
                    if result:
                        _, comments = result
                        self.save_text_post(post_data, comments, save_path)
                        print(f"  ✓ Saved text post: {filename}")
                        return True
                else:
                    self.save_text_post(post_data, [], save_path)
                    print(f"  ✓ Saved text post: {filename}")
                    return True
            
            elif post_data.get('post_hint') in ['image', 'hosted:video', 'rich:video']:
                # Media post
                url = post_data.get('url', '')
                
                # Determine file extension
                if post_data.get('is_video'):
                    # Reddit hosted video
                    media = post_data.get('media', {})
                    if media and 'reddit_video' in media:
                        url = media['reddit_video'].get('fallback_url', url)
                    ext = '.mp4'
                elif url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    ext = Path(urlparse(url).path).suffix
                else:
                    ext = '.jpg'  # default
                
                filename = f"{post_id}_{title}{ext}"
                save_path = target_dir / filename
                
                if self.download_media(url, save_path):
                    print(f"  ✓ Downloaded media: {filename}")
                    return True
            
            elif post_data.get('domain') in ['youtube.com', 'youtu.be']:
                # YouTube video - save as link for now
                filename = f"{post_id}_{title}_youtube.html"
                save_path = target_dir / filename
                self.save_link_post(post_data, save_path)
                print(f"  ✓ Saved YouTube link: {filename}")
                return True
            
            else:
                # Link post
                filename = f"{post_id}_{title}_link.html"
                save_path = target_dir / filename
                self.save_link_post(post_data, save_path)
                print(f"  ✓ Saved link post: {filename}")
                return True
        
        except Exception as e:
            print(f"  ❌ Error downloading post {post_data.get('id', 'unknown')}: {e}")
            return False
        
        return False
    
    def download_subreddit(self, subreddit: str, sort: str = "hot", 
                          time_filter: str = "day", limit: int = 100,
                          include_comments: bool = True):
        """
        Download all posts from a subreddit
        
        Args:
            subreddit: Subreddit name
            sort: Sort method
            time_filter: Time filter
            limit: Maximum posts to download
            include_comments: Whether to include comments
        """
        print(f"\n{'='*80}")
        print(f"Downloading r/{subreddit}")
        print(f"{'='*80}\n")
        
        # Fetch posts
        posts = self.fetch_subreddit(subreddit, sort, time_filter, limit)
        
        # Create output directory
        target_dir = self.output_dir / f"r_{subreddit}"
        target_dir.mkdir(exist_ok=True)
        
        # Download each post
        success_count = 0
        for i, post in enumerate(posts, 1):
            print(f"[{i}/{len(posts)}] {post['title'][:60]}...")
            if self.download_post(post, target_dir, include_comments):
                success_count += 1
        
        print(f"\n✓ Downloaded {success_count}/{len(posts)} posts from r/{subreddit}")
        print(f"📁 Saved to: {target_dir}\n")
    
    def download_user(self, username: str, sort: str = "new", limit: int = 100,
                     include_comments: bool = True):
        """
        Download all posts from a user
        
        Args:
            username: Username
            sort: Sort method
            limit: Maximum posts to download
            include_comments: Whether to include comments
        """
        print(f"\n{'='*80}")
        print(f"Downloading u/{username}")
        print(f"{'='*80}\n")
        
        # Fetch posts
        posts = self.fetch_user(username, sort, limit)
        
        # Create output directory
        target_dir = self.output_dir / f"u_{username}"
        target_dir.mkdir(exist_ok=True)
        
        # Download each post
        success_count = 0
        for i, post in enumerate(posts, 1):
            print(f"[{i}/{len(posts)}] {post['title'][:60]}...")
            if self.download_post(post, target_dir, include_comments):
                success_count += 1
        
        print(f"\n✓ Downloaded {success_count}/{len(posts)} posts from u/{username}")
        print(f"📁 Saved to: {target_dir}\n")
    
    def download_from_url(self, url: str, include_comments: bool = True):
        """
        Download a single post from URL
        
        Args:
            url: Reddit post URL
            include_comments: Whether to include comments
        """
        print(f"\n{'='*80}")
        print(f"Downloading post from URL")
        print(f"{'='*80}\n")
        
        result = self.fetch_post_with_comments(url)
        if not result:
            print("❌ Failed to fetch post")
            return
        
        post_data, comments = result
        
        # Create output directory
        subreddit = post_data.get('subreddit', 'unknown')
        target_dir = self.output_dir / f"r_{subreddit}"
        target_dir.mkdir(exist_ok=True)
        
        # Download post
        if self.download_post(post_data, target_dir, False):
            # Save comments separately if requested
            if include_comments and comments:
                post_id = post_data['id']
                title = self._sanitize_filename(post_data['title'])
                save_path = target_dir / f"{post_id}_{title}_comments.md"
                self.save_text_post(post_data, comments, save_path)
                print(f"  ✓ Saved comments")
        
        print(f"\n✓ Download complete")
        print(f"📁 Saved to: {target_dir}\n")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reddit JSON Scraper - Download Reddit content using the public JSON API"
    )
    
    parser.add_argument(
        '--subreddit', '-s',
        help='Subreddit to download (without r/)'
    )
    
    parser.add_argument(
        '--user', '-u',
        help='User to download (without u/)'
    )
    
    parser.add_argument(
        '--url',
        help='Single post URL to download'
    )
    
    parser.add_argument(
        '--sort',
        choices=['hot', 'new', 'top', 'rising', 'controversial'],
        default='hot',
        help='Sort method (default: hot)'
    )
    
    parser.add_argument(
        '--time',
        choices=['hour', 'day', 'week', 'month', 'year', 'all'],
        default='day',
        help='Time filter for top/controversial (default: day)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=100,
        help='Maximum number of posts to download (default: 100)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='reddit_downloads',
        help='Output directory (default: reddit_downloads)'
    )
    
    parser.add_argument(
        '--no-comments',
        action='store_true',
        help='Skip downloading comments'
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = RedditJSONScraper(output_dir=args.output)
    
    # Execute based on arguments
    if args.subreddit:
        scraper.download_subreddit(
            args.subreddit,
            sort=args.sort,
            time_filter=args.time,
            limit=args.limit,
            include_comments=not args.no_comments
        )
    elif args.user:
        scraper.download_user(
            args.user,
            sort=args.sort,
            limit=args.limit,
            include_comments=not args.no_comments
        )
    elif args.url:
        scraper.download_from_url(
            args.url,
            include_comments=not args.no_comments
        )
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python reddit_scraper.py --subreddit python --sort top --time week --limit 50")
        print("  python reddit_scraper.py --user spez --limit 25")
        print("  python reddit_scraper.py --url https://reddit.com/r/python/comments/abc123/")


if __name__ == "__main__":
    main()

