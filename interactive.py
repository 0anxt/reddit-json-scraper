#!/usr/bin/env python3
"""
Interactive Reddit Scraper
User-friendly conversational interface for downloading Reddit content
"""

from reddit_scraper import RedditJSONScraper
import sys

def print_banner():
    """Display welcome banner"""
    print("\n" + "=" * 70)
    print("🚀 Reddit JSON Scraper - Interactive Mode")
    print("=" * 70)
    print("Download Reddit posts, comments, images, and videos easily!")
    print("No authentication required.\n")

def print_separator():
    """Print a visual separator"""
    print("-" * 70)

def get_input(prompt, options=None, default=None):
    """
    Get user input with optional validation
    
    Args:
        prompt: Question to ask user
        options: List of valid options (case-insensitive)
        default: Default value if user presses Enter
    """
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and not default:
            print("❌ Please enter a value.\n")
            continue
        
        if options:
            if user_input.lower() in [opt.lower() for opt in options]:
                return user_input.lower()
            else:
                print(f"❌ Please choose from: {', '.join(options)}\n")
                continue
        
        return user_input

def get_number(prompt, min_val=1, max_val=1000, default=None):
    """Get a number from user with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        try:
            num = int(user_input)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"❌ Please enter a number between {min_val} and {max_val}.\n")
        except ValueError:
            print("❌ Please enter a valid number.\n")

def confirm(prompt):
    """Ask for yes/no confirmation"""
    response = get_input(f"{prompt} (yes/no)", options=['yes', 'no', 'y', 'n'], default='yes')
    return response in ['yes', 'y']

def main():
    """Main interactive flow"""
    print_banner()
    
    # Step 1: What to scrape
    print("📋 What would you like to scrape?\n")
    print("  1. Subreddit - Download posts from a subreddit")
    print("  2. User - Download posts from a specific user")
    print("  3. Single Post - Download a specific post by URL")
    print()
    
    scrape_type = get_input("Choose an option (1/2/3)", options=['1', '2', '3'])
    print()
    
    scraper = RedditJSONScraper()
    
    # Handle different scrape types
    if scrape_type == '1':
        scrape_subreddit(scraper)
    elif scrape_type == '2':
        scrape_user(scraper)
    elif scrape_type == '3':
        scrape_single_post(scraper)

def scrape_subreddit(scraper):
    """Interactive subreddit scraping"""
    print_separator()
    print("📂 SUBREDDIT SCRAPING")
    print_separator()
    print()
    
    # Get subreddit name
    print("💡 Enter the subreddit name (without 'r/')")
    print("   Examples: python, pics, AskReddit, funny")
    subreddit = get_input("Subreddit name")
    print()
    
    # Get sort method
    print("📊 How should posts be sorted?\n")
    print("  hot - Trending posts (default)")
    print("  new - Latest posts")
    print("  top - Most upvoted posts")
    print("  rising - Rising posts")
    print("  controversial - Most controversial posts")
    print()
    
    sort = get_input("Sort by", options=['hot', 'new', 'top', 'rising', 'controversial'], default='hot')
    print()
    
    # Get time filter if needed
    time_filter = 'week'
    if sort in ['top', 'controversial']:
        print("⏰ Time period for filtering:\n")
        print("  hour - Last hour")
        print("  day - Last 24 hours")
        print("  week - Last 7 days (default)")
        print("  month - Last 30 days")
        print("  year - Last year")
        print("  all - All time")
        print()
        
        time_filter = get_input("Time period", 
                               options=['hour', 'day', 'week', 'month', 'year', 'all'], 
                               default='week')
        print()
    
    # Get limit
    print("🔢 How many posts to download?")
    print("   Recommended: 5-50 posts")
    print("   Maximum: 1000 posts")
    limit = get_number("Number of posts", min_val=1, max_val=1000, default=25)
    print()
    
    # Ask about comments
    include_comments = confirm("📝 Download comments with posts?")
    print()
    
    # Custom output directory
    use_custom_dir = confirm("📁 Use custom output directory?")
    output_dir = None
    if use_custom_dir:
        output_dir = get_input("Output directory path", default="reddit_downloads")
        scraper.output_dir = Path(output_dir)
        scraper.output_dir.mkdir(exist_ok=True)
        print()
    
    # Summary
    print_separator()
    print("📋 DOWNLOAD SUMMARY")
    print_separator()
    print(f"  Subreddit: r/{subreddit}")
    print(f"  Sort: {sort}")
    if sort in ['top', 'controversial']:
        print(f"  Time: {time_filter}")
    print(f"  Limit: {limit} posts")
    print(f"  Comments: {'Yes' if include_comments else 'No'}")
    print(f"  Output: {scraper.output_dir}")
    print_separator()
    print()
    
    # Confirm and start
    if not confirm("🚀 Start download?"):
        print("\n❌ Download cancelled.\n")
        return
    
    print("\n" + "=" * 70)
    print("⬇️  DOWNLOADING...")
    print("=" * 70 + "\n")
    
    # Execute download
    try:
        scraper.download_subreddit(
            subreddit=subreddit,
            sort=sort,
            time_filter=time_filter,
            limit=limit,
            include_comments=include_comments
        )
        
        print("\n" + "=" * 70)
        print("✅ DOWNLOAD COMPLETE!")
        print("=" * 70)
        print(f"📁 Files saved to: {scraper.output_dir}/r_{subreddit}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)

def scrape_user(scraper):
    """Interactive user scraping"""
    print_separator()
    print("👤 USER SCRAPING")
    print_separator()
    print()
    
    # Get username
    print("💡 Enter the Reddit username (without 'u/')")
    print("   Examples: spez, AutoModerator")
    username = get_input("Username")
    print()
    
    # Get sort method
    print("📊 How should posts be sorted?\n")
    print("  new - Latest posts (default)")
    print("  hot - Trending posts")
    print("  top - Most upvoted posts")
    print("  controversial - Most controversial posts")
    print()
    
    sort = get_input("Sort by", options=['new', 'hot', 'top', 'controversial'], default='new')
    print()
    
    # Get limit
    print("🔢 How many posts to download?")
    print("   Recommended: 5-50 posts")
    limit = get_number("Number of posts", min_val=1, max_val=1000, default=25)
    print()
    
    # Ask about comments
    include_comments = confirm("📝 Download comments with posts?")
    print()
    
    # Summary
    print_separator()
    print("📋 DOWNLOAD SUMMARY")
    print_separator()
    print(f"  User: u/{username}")
    print(f"  Sort: {sort}")
    print(f"  Limit: {limit} posts")
    print(f"  Comments: {'Yes' if include_comments else 'No'}")
    print(f"  Output: {scraper.output_dir}")
    print_separator()
    print()
    
    # Confirm and start
    if not confirm("🚀 Start download?"):
        print("\n❌ Download cancelled.\n")
        return
    
    print("\n" + "=" * 70)
    print("⬇️  DOWNLOADING...")
    print("=" * 70 + "\n")
    
    # Execute download
    try:
        scraper.download_user(
            username=username,
            sort=sort,
            limit=limit,
            include_comments=include_comments
        )
        
        print("\n" + "=" * 70)
        print("✅ DOWNLOAD COMPLETE!")
        print("=" * 70)
        print(f"📁 Files saved to: {scraper.output_dir}/u_{username}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)

def scrape_single_post(scraper):
    """Interactive single post scraping"""
    print_separator()
    print("🔗 SINGLE POST DOWNLOAD")
    print_separator()
    print()
    
    # Get URL
    print("💡 Enter the Reddit post URL")
    print("   Examples:")
    print("   - https://reddit.com/r/pics/comments/abc123/")
    print("   - https://www.reddit.com/r/AskReddit/comments/xyz789/what_is/")
    print()
    
    url = get_input("Post URL")
    print()
    
    # Ask about comments
    include_comments = confirm("📝 Download comments with the post?")
    print()
    
    # Summary
    print_separator()
    print("📋 DOWNLOAD SUMMARY")
    print_separator()
    print(f"  URL: {url}")
    print(f"  Comments: {'Yes' if include_comments else 'No'}")
    print(f"  Output: {scraper.output_dir}")
    print_separator()
    print()
    
    # Confirm and start
    if not confirm("🚀 Start download?"):
        print("\n❌ Download cancelled.\n")
        return
    
    print("\n" + "=" * 70)
    print("⬇️  DOWNLOADING...")
    print("=" * 70 + "\n")
    
    # Execute download
    try:
        scraper.download_from_url(url, include_comments=include_comments)
        
        print("\n" + "=" * 70)
        print("✅ DOWNLOAD COMPLETE!")
        print("=" * 70)
        print(f"📁 Files saved to: {scraper.output_dir}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)

