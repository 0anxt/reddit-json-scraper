# 🚀 Reddit JSON Scraper

> A simple, powerful Python tool to download Reddit posts, comments, images, and videos using Reddit's public JSON API. **No login or API keys required!**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 📥 **Download from subreddits** - Get posts sorted by hot, new, top, rising, or controversial
- 👤 **Download user posts** - Archive all posts from any Reddit user
- 💬 **Full comment extraction** - Save comment threads with nested replies (up to 5 levels)
- 🖼️ **All media types** - Images (JPG, PNG), videos (MP4), GIFs, and more
- 🔗 **Link preservation** - Save link posts as HTML redirects
- ⚡ **Fast and efficient** - Rate limiting to avoid IP bans
- 🎯 **No authentication** - Uses Reddit's public JSON API
- 📝 **Markdown format** - Posts and comments saved in readable Markdown
- 🔧 **CLI and Python API** - Use from command line or import as a library

## 🎬 Quick Start

### Installation

**1. Clone this repository**
```bash
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper
```

**2. Create a virtual environment (recommended)**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

That's it! You're ready to go. 🎉

> 💡 **Having installation issues?** See the detailed [INSTALL.md](INSTALL.md) guide for:
> - Virtual environment setup
> - Platform-specific instructions (Linux/Mac/Windows)
> - Troubleshooting common errors
> - Docker installation

### Basic Usage

#### 🎯 Interactive Mode (Recommended for Beginners)

Just run the interactive script and answer the questions:

```bash
python interactive.py
```

The script will guide you through:
1. What to scrape (subreddit, user, or single post)
2. Sorting options
3. Number of posts
4. Whether to include comments
5. Confirmation before downloading

**Perfect for first-time users!** No need to remember command-line arguments.

#### ⚡ Command-Line Mode (For Advanced Users)

**Download top posts from a subreddit:**
```bash
python reddit_scraper.py --subreddit python --sort top --time week --limit 25
```

**Download posts from a user:**
```bash
python reddit_scraper.py --user username --limit 10
```

**Download a specific post:**
```bash
python reddit_scraper.py --url "https://reddit.com/r/pics/comments/abc123/"
```

## 📖 Detailed Usage

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--subreddit` | `-s` | Subreddit to download (without r/) | `--subreddit python` |
| `--user` | `-u` | User to download (without u/) | `--user spez` |
| `--url` | | Single post URL to download | `--url "https://..."` |
| `--sort` | | Sort: hot, new, top, rising, controversial | `--sort top` |
| `--time` | | Time: hour, day, week, month, year, all | `--time week` |
| `--limit` | `-l` | Max posts to download | `--limit 50` |
| `--output` | `-o` | Output directory | `--output downloads` |
| `--no-comments` | | Skip downloading comments (faster) | `--no-comments` |

### Examples

**1. Archive a subreddit's top posts this month**
```bash
python reddit_scraper.py --subreddit AskReddit --sort top --time month --limit 100
```

**2. Download new posts (good for monitoring)**
```bash
python reddit_scraper.py --subreddit news --sort new --limit 25
```

**3. Get images from r/pics (skip comments for speed)**
```bash
python reddit_scraper.py --subreddit pics --sort hot --limit 50 --no-comments
```

**4. Download a specific post with all comments**
```bash
python reddit_scraper.py --url "https://reddit.com/r/nextfuckinglevel/comments/1o8ze9o/"
```

**5. Custom output directory**
```bash
python reddit_scraper.py --subreddit python --output my_python_archive --limit 30
```

## 🐍 Python API

You can also use the scraper in your Python scripts:

```python
from reddit_scraper import RedditJSONScraper

# Create scraper instance
scraper = RedditJSONScraper(output_dir="downloads")

# Download from subreddit
scraper.download_subreddit(
    subreddit="python",
    sort="top",
    time_filter="week",
    limit=50,
    include_comments=True
)

# Download from user
scraper.download_user(username="spez", limit=25)

# Download single post
scraper.download_from_url("https://reddit.com/r/pics/comments/abc123/")

# Fetch posts without downloading (for analysis)
posts = scraper.fetch_subreddit("python", sort="hot", limit=100)
for post in posts:
    print(f"{post['title']} - {post['score']} upvotes")
```

See [examples.py](examples.py) for more usage examples!

## 📁 Output Structure

Downloaded content is organized like this:

```
reddit_downloads/
├── r_python/
│   ├── 1abc123_Amazing_Python_Tutorial.md          # Text post with comments
│   ├── 1def456_Cool_Screenshot.png                 # Image
│   ├── 1ghi789_Funny_Video.mp4                     # Video
│   └── 1jkl012_Interesting_Article_link.html       # Link post
├── r_pics/
│   └── ...
└── u_username/
    └── ...
```

### File Naming

Files are named: `{post_id}_{sanitized_title}.{extension}`

- **Post ID** - Reddit's unique ID (prevents duplicates)
- **Title** - Post title with special characters removed
- **Extension** - Based on content type (.md, .jpg, .mp4, .html)

### Content Formats

**Text Posts (.md)** - Markdown files with:
- Post title, author, score, timestamp
- Full post content
- All comments with nested replies
- Formatted for easy reading

**Images** - Downloaded in original format (JPG, PNG, etc.)

**Videos** - MP4 format, including Reddit-hosted videos

**Link Posts (.html)** - HTML files that auto-redirect to the original URL

## 🔧 How It Works

This scraper uses **Reddit's public JSON API** - no authentication needed!

Simply append `.json` to any Reddit URL:
- `https://reddit.com/r/python/top.json` - Top posts
- `https://reddit.com/r/python/comments/abc123.json` - Post with comments

The scraper:
1. Fetches JSON data from Reddit
2. Parses posts and comments
3. Downloads media files
4. Saves everything in organized folders

**Rate Limiting:** Automatically waits 2 seconds between requests to avoid IP bans. If rate-limited (429 error), waits 60 seconds and retries.

## ⚠️ Important Notes

### What You Can Download
- ✅ Any public subreddit
- ✅ Any public user's posts
- ✅ Any public post with comments
- ✅ Images, videos, GIFs
- ✅ Text posts with full formatting
- ✅ Link posts

### What You Cannot Download
- ❌ Private subreddits (requires login)
- ❌ Deleted or removed posts
- ❌ User-specific content (saved posts, messages)
- ❌ Content from banned/quarantined subreddits

### Best Practices
- 🕐 Use reasonable limits (don't download 10,000 posts at once)
- ⏱️ The scraper has built-in rate limiting - don't modify it
- 💾 Large downloads can take significant time and disk space
- 🤝 Be respectful of Reddit's servers

## 🆚 Comparison with Other Tools

| Feature | This Scraper | easy-reddit-downloader | Gallery-dl |
|---------|-------------|----------------------|-----------|
| Language | Python | Node.js | Python |
| Auth Required | ❌ No | ❌ No | ❌ No |
| Comments | ✅ Nested | ✅ Yes | ❌ No |
| CLI | ✅ Args | ✅ Interactive | ✅ Args |
| Python API | ✅ Yes | ❌ No | ⚠️ Limited |
| Dependencies | 1 (requests) | Multiple | Multiple |
| Setup Time | < 1 min | ~2 min | ~2 min |

## 🐛 Troubleshooting

**"No items returned" or "403 Forbidden"**
- Subreddit might be private or doesn't exist
- Try a different subreddit or check the spelling
- Reddit might be temporarily blocking requests

**"Rate limited (429)"**
- The scraper will automatically wait and retry
- If it persists, wait a few minutes before running again

**"No module named 'requests'"**
- Install the dependency: `pip install requests`

**Downloads are slow**
- This is normal - the scraper waits 2 seconds between requests
- Use `--no-comments` to skip comments for faster downloads
- Reduce `--limit` for smaller batches

**Some posts didn't download**
- Posts may be deleted, removed, or failed to load
- Check the output for error messages
- This is expected - not all posts will download successfully

## 📝 Examples

Check out [examples.py](examples.py) for 8 different usage examples:
1. Basic subreddit download
2. Multiple subreddits
3. User posts
4. Single post with comments
5. Fetch and analyze (no download)
6. Filter by score
7. Media-only downloads
8. Custom data processing

Run examples:
```bash
python examples.py
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests
- 📖 Improve documentation

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

This tool is for **educational and personal use only**. Please:
- Respect Reddit's [Terms of Service](https://www.redditinc.com/policies/user-agreement)
- Don't use for commercial purposes without permission
- Don't abuse Reddit's servers with excessive requests
- Be a good internet citizen! 🌐

## 🙏 Acknowledgments

- Inspired by [easy-reddit-downloader](https://github.com/josephrcox/easy-reddit-downloader)
- Uses Reddit's public JSON API
- Built with Python and the `requests` library

## 💬 Support

- 📖 Check the [Quick Start Guide](QUICKSTART.md)
- 🐛 [Open an issue](https://github.com/yourusername/reddit-json-scraper/issues)
- 💡 [View examples](examples.py)

---

**Made with ❤️ for the Reddit community**

If you find this useful, give it a ⭐ on GitHub!

