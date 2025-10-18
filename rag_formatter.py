"""
RAG-Optimized Format Generator
Converts Reddit posts to RAG-friendly markdown format
"""

from typing import List, Dict
from pathlib import Path
from datetime import datetime
from collections import Counter


def save_text_post_rag(post_data: Dict, comments: List[Dict], save_path: Path):
    """
    Save text post in RAG-optimized format
    
    Args:
        post_data: Post data dictionary
        comments: List of comment dictionaries
        save_path: Path to save the markdown file
    """
    with open(save_path, 'w', encoding='utf-8') as f:
        # YAML Frontmatter
        f.write("---\n")
        f.write("metadata:\n")
        f.write("  source: reddit\n")
        f.write("  source_type: reddit_post\n")
        f.write(f"  post_id: {post_data['id']}\n")
        f.write(f"  subreddit: {post_data['subreddit']}\n")
        f.write(f"  author: {post_data['author']}\n")
        f.write(f"  created_utc: {post_data['created_utc']}\n")
        f.write(f"  created_date: {datetime.fromtimestamp(post_data['created_utc']).strftime('%Y-%m-%d')}\n")
        f.write(f"  score: {post_data['score']}\n")
        f.write(f"  num_comments: {post_data.get('num_comments', len(comments))}\n")
        f.write(f"  post_type: text\n")
        f.write(f"  url: https://reddit.com{post_data['permalink']}\n")
        f.write(f"  title: {post_data['title']}\n")
        f.write(f"  has_comments: {len(comments) > 0}\n")
        f.write(f"  comment_count: {len(comments)}\n")
        f.write(f"  scraped_date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"  flair: {post_data.get('link_flair_text', 'null')}\n")
        f.write(f"  awards: {post_data.get('total_awards_received', 'null')}\n")
        f.write("---\n\n")
        
        # Post Content Section
        f.write("# Post Content\n\n")
        f.write(f"**Title:** {post_data['title']}\n\n")
        f.write(f"**Subreddit:** r/{post_data['subreddit']}\n\n")
        f.write(f"**Author:** u/{post_data['author']}\n\n")
        created_time = datetime.fromtimestamp(post_data['created_utc'])
        f.write(f"**Posted:** {created_time.strftime('%B %d, %Y at %I:%M %p')} UTC\n\n")
        f.write(f"**Score:** {post_data['score']} upvotes\n\n")
        
        if post_data.get('selftext'):
            f.write(f"**Post Body:**\n\n{post_data['selftext']}\n\n")
        else:
            f.write("**Post Body:** (No text content)\n\n")
        
        f.write("---\n\n")
        
        # Discussion Summary
        if comments:
            f.write("# Discussion Summary\n\n")
            summary = generate_discussion_summary(post_data, comments)
            f.write(summary)
            f.write("\n---\n\n")
            
            # Comments Analysis
            f.write("# Comments Analysis\n\n")
            f.write("## Top Comments (by score)\n\n")
            write_top_comments(f, comments)
            f.write("\n---\n\n")
            
            # All Comments Flat List
            f.write("# All Comments (Flat List for Search)\n\n")
            write_flat_comments(f, comments)
            f.write("\n---\n\n")
            
            # Statistics
            f.write("# Statistics\n\n")
            write_statistics(f, post_data, comments)
            f.write("\n---\n\n")
        
        # Tags
        f.write("# Tags\n\n")
        tags = generate_tags(post_data, comments)
        f.write(", ".join(tags))
        f.write("\n\n---\n\n")
        
        # Embeddings Optimization
        f.write("# Embeddings Optimization\n\n")
        f.write("**Context for RAG:**\n")
        context = generate_rag_context(post_data, comments)
        f.write(context)
        f.write("\n\n")
        
        f.write("**Key Entities:**\n")
        entities = generate_key_entities(post_data)
        for key, value in entities.items():
            f.write(f"- {key}: {value}\n")
        f.write("\n")
        
        f.write("**Searchable Phrases:**\n")
        phrases = generate_searchable_phrases(post_data)
        for phrase in phrases:
            f.write(f"- \"{phrase}\"\n")
        f.write("\n---\n\n")
        
        # Footer
        f.write("**Document Type:** reddit_post_with_comments\n")
        f.write("**Vector Database Ready:** Yes\n")
        f.write("**Chunk-Friendly:** Yes\n")
        f.write("**Metadata Complete:** Yes\n")


def generate_discussion_summary(post_data: Dict, comments: List[Dict]) -> str:
    """Generate a summary of the discussion"""
    title = post_data['title']
    subreddit = post_data['subreddit']
    score = post_data['score']
    num_comments = len(comments)
    
    summary = f"This post in r/{subreddit} titled \"{title}\" received {score} upvotes and {num_comments} comments. "
    
    if post_data.get('selftext'):
        summary += "The post discusses "
        # Extract first sentence or first 150 chars
        text = post_data['selftext']
        first_sentence = text.split('.')[0] if '.' in text else text[:150]
        summary += first_sentence.strip() + "...\n\n"
    
    # Analyze comment sentiment/themes
    if comments:
        top_commenters = get_top_commenters(comments)
        summary += f"**Most Active Participants:**\n"
        for user, count in top_commenters[:3]:
            summary += f"- u/{user} ({count} comments)\n"
    
    return summary


def write_top_comments(f, comments: List[Dict], limit: int = 5):
    """Write top comments by score"""
    sorted_comments = sorted(comments, key=lambda x: x['score'], reverse=True)
    for i, comment in enumerate(sorted_comments[:limit], 1):
        f.write(f"**{i}. u/{comment['author']} ({comment['score']} points):**\n")
        f.write(f"{comment['body']}\n\n")


def write_flat_comments(f, comments: List[Dict]):
    """Write all comments in a flat list"""
    flat_list = flatten_comments(comments)
    for i, comment in enumerate(flat_list, 1):
        f.write(f"{i}. u/{comment['author']}: \"{comment['body']}\" ({comment['score']} points)\n")


def flatten_comments(comments: List[Dict], result: List[Dict] = None) -> List[Dict]:
    """Flatten nested comments into a single list"""
    if result is None:
        result = []
    
    for comment in comments:
        result.append(comment)
        if comment.get('replies'):
            flatten_comments(comment['replies'], result)
    
    return result


def write_statistics(f, post_data: Dict, comments: List[Dict]):
    """Write statistics section"""
    flat = flatten_comments(comments)
    total_comments = len(flat)
    top_level = len(comments)
    
    # Calculate average thread depth
    depths = [get_comment_depth(c) for c in comments]
    avg_depth = sum(depths) / len(depths) if depths else 0
    
    # Most active user
    commenters = [c['author'] for c in flat]
    if commenters:
        most_active = Counter(commenters).most_common(1)[0]
        most_active_user = f"u/{most_active[0]} ({most_active[1]} comments)"
    else:
        most_active_user = "None"
    
    f.write(f"- **Total Comments:** {total_comments}\n")
    f.write(f"- **Top-Level Comments:** {top_level}\n")
    f.write(f"- **Average Thread Depth:** {avg_depth:.1f}\n")
    f.write(f"- **Post Score:** {post_data['score']} upvotes\n")
    f.write(f"- **Most Active User:** {most_active_user}\n")


def get_comment_depth(comment: Dict, depth: int = 1) -> int:
    """Get the maximum depth of a comment thread"""
    if not comment.get('replies'):
        return depth
    return max(get_comment_depth(reply, depth + 1) for reply in comment['replies'])


def get_top_commenters(comments: List[Dict]) -> List[tuple]:
    """Get list of (username, comment_count) tuples"""
    flat = flatten_comments(comments)
    commenters = [c['author'] for c in flat]
    return Counter(commenters).most_common(10)


def generate_tags(post_data: Dict, comments: List[Dict]) -> List[str]:
    """Generate tags for the post"""
    tags = []
    
    # Add subreddit as tag
    tags.append(post_data['subreddit'].lower())
    
    # Extract keywords from title (simple approach)
    title_words = post_data['title'].lower().split()
    # Filter out common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
    keywords = [w.strip('.,!?":;()[]{}') for w in title_words if w not in stop_words and len(w) > 3]
    tags.extend(keywords[:5])
    
    return tags


def generate_rag_context(post_data: Dict, comments: List[Dict]) -> str:
    """Generate context paragraph for RAG embeddings"""
    subreddit = post_data['subreddit']
    title = post_data['title']
    score = post_data['score']
    num_comments = len(flatten_comments(comments))
    
    context = f"This is a Reddit post from r/{subreddit} titled \"{title}\". "
    context += f"It received {score} upvotes and {num_comments} comments. "
    
    if post_data.get('selftext'):
        # First 200 chars of post body
        body_preview = post_data['selftext'][:200].strip()
        context += f"The post discusses: {body_preview}... "
    
    if comments:
        context += f"The discussion includes {len(comments)} top-level comments with various perspectives."
    
    return context


def generate_key_entities(post_data: Dict) -> Dict[str, str]:
    """Generate key entities for the post"""
    return {
        "Subreddit": post_data['subreddit'],
        "Author": post_data['author'],
        "Post Type": "Text/Discussion",
        "Topic": post_data['title'][:50] + "..." if len(post_data['title']) > 50 else post_data['title'],
        "Engagement": f"{post_data['score']} upvotes"
    }


def generate_searchable_phrases(post_data: Dict) -> List[str]:
    """Generate searchable phrases from the post"""
    phrases = []
    
    # Add title
    phrases.append(post_data['title'].lower())
    
    # Add subreddit-specific phrase
    phrases.append(f"r/{post_data['subreddit']} discussion")
    
    # Extract key phrases from title (simple bigrams/trigrams)
    words = post_data['title'].lower().split()
    if len(words) >= 2:
        phrases.append(" ".join(words[:2]))
    if len(words) >= 3:
        phrases.append(" ".join(words[:3]))
    
    return phrases[:5]
