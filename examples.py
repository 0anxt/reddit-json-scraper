#!/usr/bin/env python3
"""
Example usage scripts for Reddit JSON Scraper
"""

from reddit_scraper import RedditJSONScraper

def example_1_basic_subreddit():
    """Download top posts from a subreddit"""
    print("Example 1: Download top posts from r/python")
    print("-" * 60)
    
    scraper = RedditJSONScraper(output_dir="examples/example1")
    scraper.download_subreddit(
        subreddit="python",
        sort="top",
        time_filter="week",
        limit=10,
        include_comments=True
    )

def example_2_multiple_subreddits():
    """Download from multiple subreddits"""
    print("\nExample 2: Download from multiple subreddits")
    print("-" * 60)
    
    scraper = RedditJSONScraper(output_dir="examples/example2")
    
    subreddits = ["python", "learnpython", "programming"]
    for sub in subreddits:
        scraper.download_subreddit(
            subreddit=sub,
            sort="hot",
            limit=5,
            include_comments=False  # Faster without comments
        )

def example_3_user_posts():
    """Download posts from a specific user"""
    print("\nExample 3: Download user posts")
    print("-" * 60)
    
    scraper = RedditJSONScraper(output_dir="examples/example3")
    scraper.download_user(
        username="AutoModerator",
        sort="new",
        limit=10,
        include_comments=False
    )

def example_4_single_post():
    """Download a specific post with comments"""
    print("\nExample 4: Download single post")
    print("-" * 60)
    
    scraper = RedditJSONScraper(output_dir="examples/example4")
    scraper.download_from_url(
        url="https://reddit.com/r/nextfuckinglevel/comments/1o8ze9o/",
        include_comments=True
    )

def example_5_fetch_only():
    """Fetch posts without downloading (for analysis)"""
    print("\nExample 5: Fetch and analyze posts")
    print("-" * 60)
    
    scraper = RedditJSONScraper()
    
    # Fetch top posts
    posts = scraper.fetch_subreddit("python", sort="top", time_filter="month", limit=50)
    
    # Analyze
    total_score = sum(post['score'] for post in posts)
    avg_score = total_score / len(posts) if posts else 0
    
    print(f"Fetched {len(posts)} posts")
    print(f"Average score: {avg_score:.1f}")
    print(f"Total score: {total_score}")
    
    # Find most popular
    if posts:
        top_post = max(posts, key=lambda p: p['score'])
        print(f"\nMost popular post:")
        print(f"  Title: {top_post['title']}")
        print(f"  Score: {top_post['score']}")
        print(f"  Author: u/{top_post['author']}")

def example_6_filter_by_score():
    """Download only highly-voted posts"""
    print("\nExample 6: Download high-score posts only")
    print("-" * 60)
    
    scraper = RedditJSONScraper(output_dir="examples/example6")
    
    # Fetch posts
    posts = scraper.fetch_subreddit("pics", sort="top", time_filter="week", limit=100)
    
    # Filter by score
    high_score_posts = [p for p in posts if p['score'] > 5000]
    
    print(f"Found {len(high_score_posts)} posts with >5000 upvotes")
    
    # Download filtered posts
    from pathlib import Path
    target_dir = scraper.output_dir / "r_pics_filtered"
    
    for post in high_score_posts:
        scraper.download_post(post, target_dir, include_comments=False)

def example_7_media_only():
    """Download only media posts (images/videos)"""
    print("\nExample 7: Download media posts only")
    print("-" * 60)
    
    scraper = RedditJSONScraper(output_dir="examples/example7")
    
    # Fetch posts
    posts = scraper.fetch_subreddit("pics", sort="hot", limit=50)
    
    # Filter media posts
    media_posts = [p for p in posts if p.get('post_hint') in ['image', 'hosted:video', 'rich:video']]
    
    print(f"Found {len(media_posts)} media posts")
    
    # Download
    from pathlib import Path
    target_dir = scraper.output_dir / "r_pics_media"
    
    for post in media_posts:
        scraper.download_post(post, target_dir, include_comments=False)

def example_8_custom_processing():
    """Custom processing of post data"""
    print("\nExample 8: Custom data processing")
    print("-" * 60)
    
    scraper = RedditJSONScraper()
    
    # Fetch posts with comments
    url = "https://reddit.com/r/AskReddit/comments/1o8ze9o/.json"
    result = scraper.fetch_post_with_comments(url)
    
    if result:
        post_data, comments = result
        
        print(f"Post: {post_data['title']}")
        print(f"Comments: {len(comments)}")
        
        # Analyze comment sentiment (simple word count)
        positive_words = ['great', 'awesome', 'love', 'excellent', 'amazing']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible']
        
        positive_count = 0
        negative_count = 0
        
        for comment in comments:
            body = comment['body'].lower()
            positive_count += sum(1 for word in positive_words if word in body)
            negative_count += sum(1 for word in negative_words if word in body)
        
        print(f"\nSentiment analysis:")
        print(f"  Positive words: {positive_count}")
        print(f"  Negative words: {negative_count}")

if __name__ == "__main__":
    # Run all examples
    print("=" * 60)
    print("Reddit JSON Scraper - Example Usage")
    print("=" * 60)
    
    # Uncomment the examples you want to run
    
    # example_1_basic_subreddit()
    # example_2_multiple_subreddits()
    # example_3_user_posts()
    # example_4_single_post()
    example_5_fetch_only()
    # example_6_filter_by_score()
    # example_7_media_only()
    # example_8_custom_processing()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)

