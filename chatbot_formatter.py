"""
RAG-Chatbot Format Generator
Formats Reddit posts according to custom chatbot template
"""

from typing import List, Dict
from pathlib import Path
from datetime import datetime


def save_text_post_chatbot(post_data: Dict, comments: List[Dict], save_path: Path):
    """
    Save text post in RAG-chatbot format (custom template)
    
    Args:
        post_data: Post data dictionary
        comments: List of comment dictionaries
        save_path: Path to save the markdown file
    """
    with open(save_path, 'w', encoding='utf-8') as f:
        # YAML Frontmatter
        f.write("---\n")
        f.write(f"source: \"Reddit r/{post_data['subreddit']}\"\n")
        f.write("type: \"discussion\"\n")
        
        # Extract topic from title (simplified)
        topic = extract_topic(post_data['title'])
        f.write(f"topic: \"{topic}\"\n")
        
        # Generate subtopics
        subtopics = generate_subtopics(post_data, comments)
        f.write(f"subtopics: \"{','.join(subtopics)}\"\n")
        
        # Date
        created_date = datetime.fromtimestamp(post_data['created_utc']).strftime('%Y-%m-%d')
        f.write(f"date: \"{created_date}\"\n")
        
        # URL
        f.write(f"url: \"https://reddit.com{post_data['permalink']}\"\n")
        f.write("---\n\n")
        
        # Title
        f.write(f"# {post_data['title']}\n\n")
        
        # Author
        f.write(f"**Posted by:** u/{post_data['author']}\n\n")
        
        # Main Content
        f.write("## Main Content\n\n")
        if post_data.get('selftext'):
            f.write(f"{post_data['selftext']}\n\n")
        else:
            f.write("*(This post has no body text)*\n\n")
        
        # Key Points
        f.write("## Key Points\n\n")
        key_points = extract_key_points(post_data)
        for point in key_points:
            f.write(f"- {point}\n")
        f.write("\n")
        
        # Valuable Comments
        if comments:
            f.write("## Valuable Comments\n\n")
            valuable_comments = get_valuable_comments(comments, limit=5)
            for comment in valuable_comments:
                f.write(f"### Comment by u/{comment['author']}\n\n")
                f.write(f"{comment['body']}\n\n")
                
                # Extract key insight
                insight = extract_key_insight(comment)
                f.write(f"**Key insight:** {insight}\n\n")
        
        # Practical Application
        f.write("## Practical Application\n\n")
        application = generate_practical_application(post_data, comments)
        f.write(f"{application}\n\n")
        
        # Common Misconceptions Addressed
        if has_misconceptions(post_data, comments):
            f.write("## Common Misconceptions Addressed\n\n")
            misconceptions = extract_misconceptions(post_data, comments)
            for misconception in misconceptions:
                f.write(f"{misconception}\n\n")


def extract_topic(title: str) -> str:
    """Extract main topic from title"""
    # Convert to lowercase and remove special characters
    topic = title.lower()
    # Remove common words
    stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
    words = [w for w in topic.split() if w not in stop_words and len(w) > 3]
    
    # Take first 2-3 meaningful words
    if len(words) >= 2:
        return '_'.join(words[:2])
    elif len(words) == 1:
        return words[0]
    else:
        return 'discussion'


def generate_subtopics(post_data: Dict, comments: List[Dict]) -> List[str]:
    """Generate subtopics from post and comments"""
    subtopics = []
    
    # Extract from title
    title_lower = post_data['title'].lower()
    
    # Common manifestation keywords
    keywords = {
        'visualiz': 'visualization',
        'affirm': 'affirmations',
        'sats': 'sats',
        'revision': 'revision',
        'mental': 'mental_diet',
        'feeling': 'feeling',
        'assumption': 'assumptions',
        'state': 'state',
        'persist': 'persistence',
        'faith': 'faith',
        'belief': 'belief',
        'manifest': 'manifestation',
        'technique': 'techniques',
        'neville': 'neville_goddard',
        'living': 'living_in_the_end',
        'end': 'living_in_the_end',
        'enjoy': 'present_tense',
        'goal': 'goals',
        'success': 'success',
        'sp': 'specific_person',
        'relationship': 'relationships',
        'money': 'money',
        'health': 'health',
        'career': 'career'
    }
    
    # Check title and body for keywords
    text_to_check = title_lower
    if post_data.get('selftext'):
        text_to_check += ' ' + post_data['selftext'].lower()
    
    for keyword, tag in keywords.items():
        if keyword in text_to_check and tag not in subtopics:
            subtopics.append(tag)
    
    # Limit to 5 subtopics
    return subtopics[:5] if subtopics else ['general']


def extract_key_points(post_data: Dict) -> List[str]:
    """Extract key points from post content"""
    key_points = []
    
    if not post_data.get('selftext'):
        # If no body, extract from title
        key_points.append(f"Discussion topic: {post_data['title']}")
        return key_points
    
    text = post_data['selftext']
    lines = text.split('\n')
    
    # Look for bullet points or numbered lists
    for line in lines:
        line = line.strip()
        # Check if it's a bullet point or numbered item
        if line.startswith(('-', '*', '•')) or (len(line) > 0 and line[0].isdigit() and '.' in line[:3]):
            # Clean up the bullet/number
            clean_line = line.lstrip('-*•0123456789. ').strip()
            if len(clean_line) > 10:  # Meaningful length
                key_points.append(clean_line)
    
    # If no bullet points found, extract first few sentences
    if not key_points:
        sentences = text.split('.')
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if len(sentence) > 20:
                key_points.append(sentence)
    
    # Limit to 5 key points
    return key_points[:5] if key_points else ["Main discussion point from the post"]


def get_valuable_comments(comments: List[Dict], limit: int = 5) -> List[Dict]:
    """Get the most valuable comments based on score"""
    # Sort by score
    sorted_comments = sorted(comments, key=lambda x: x['score'], reverse=True)
    
    # Filter out very short comments
    valuable = [c for c in sorted_comments if len(c['body']) > 50]
    
    return valuable[:limit]


def extract_key_insight(comment: Dict) -> str:
    """Extract key insight from a comment"""
    body = comment['body']
    
    # Look for key phrases
    key_phrases = [
        'the key is',
        'what worked for me',
        'the important thing',
        'what helped me',
        'the difference is',
        'what changed everything',
        'the secret is',
        'what finally worked'
    ]
    
    body_lower = body.lower()
    for phrase in key_phrases:
        if phrase in body_lower:
            # Find the sentence containing this phrase
            sentences = body.split('.')
            for sentence in sentences:
                if phrase in sentence.lower():
                    return sentence.strip() + '.'
    
    # If no key phrase found, take first sentence or summarize
    first_sentence = body.split('.')[0].strip()
    if len(first_sentence) > 100:
        # Too long, create a summary
        return f"Provides perspective on {extract_main_theme(body)}"
    else:
        return first_sentence + '.' if first_sentence else "Adds valuable perspective to the discussion"


def extract_main_theme(text: str) -> str:
    """Extract main theme from text"""
    text_lower = text.lower()
    
    themes = {
        'visualiz': 'visualization techniques',
        'affirm': 'affirmations',
        'feeling': 'the importance of feeling',
        'state': 'state of being',
        'assumption': 'assumptions',
        'persist': 'persistence',
        'living in the end': 'living in the end',
        'mental diet': 'mental diet',
        'revision': 'revision',
        'sats': 'SATS technique'
    }
    
    for keyword, theme in themes.items():
        if keyword in text_lower:
            return theme
    
    return 'manifestation practice'


def generate_practical_application(post_data: Dict, comments: List[Dict]) -> str:
    """Generate practical application section"""
    # Check if post already has practical advice
    if post_data.get('selftext'):
        text_lower = post_data['selftext'].lower()
        if any(word in text_lower for word in ['how to', 'steps', 'practice', 'exercise', 'try this']):
            return "See the main content above for practical steps and exercises."
    
    # Generate generic but useful application
    topic = extract_topic(post_data['title'])
    
    application = f"**How to apply this teaching:**\n\n"
    application += "1. **Understand the concept:** Review the main points above and ensure you grasp the core teaching.\n\n"
    application += "2. **Reflect on your current practice:** Consider how this insight relates to your manifestation journey.\n\n"
    application += "3. **Implement gradually:** Start incorporating this understanding into your daily practice.\n\n"
    application += "4. **Observe results:** Notice how this shift in understanding affects your manifestations.\n\n"
    application += "5. **Adjust as needed:** Refine your approach based on your personal experience."
    
    return application


def has_misconceptions(post_data: Dict, comments: List[Dict]) -> bool:
    """Check if post addresses misconceptions"""
    if not post_data.get('selftext'):
        return False
    
    text_lower = post_data['selftext'].lower()
    
    misconception_indicators = [
        'misconception',
        'not what you think',
        'does not mean',
        'doesn\'t mean',
        'common mistake',
        'wrong',
        'misunderstand',
        'clarify',
        'confusion',
        'actually means'
    ]
    
    return any(indicator in text_lower for indicator in misconception_indicators)


def extract_misconceptions(post_data: Dict, comments: List[Dict]) -> List[str]:
    """Extract misconceptions addressed in the post"""
    misconceptions = []
    
    if not post_data.get('selftext'):
        return misconceptions
    
    text = post_data['selftext']
    lines = text.split('\n')
    
    # Look for patterns like "X does NOT mean" or "Misconception:"
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        if 'does not mean' in line_lower or 'doesn\'t mean' in line_lower:
            misconceptions.append(f"**Addressed:** {line.strip()}")
        
        elif 'misconception' in line_lower and i + 1 < len(lines):
            misconceptions.append(f"**Misconception:** {lines[i+1].strip()}")
        
        elif 'common mistake' in line_lower:
            misconceptions.append(f"**Common mistake:** {line.strip()}")
    
    # If no specific misconceptions found but post addresses them
    if not misconceptions and has_misconceptions(post_data, comments):
        misconceptions.append("**Clarification:** This post addresses common misunderstandings about the topic. See main content for details.")
    
    return misconceptions[:3]  # Limit to 3

