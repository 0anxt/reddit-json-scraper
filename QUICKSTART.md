# ⚡ Quick Start Guide

Get started with Reddit JSON Scraper in **under 2 minutes**!

## 🚀 Installation (30 seconds)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/reddit-json-scraper.git
cd reddit-json-scraper

# 2. Install dependency
pip install requests
```

Done! ✅

## 💡 Your First Download (30 seconds)

Try this command to download 5 top posts from r/python:

```bash
python reddit_scraper.py --subreddit python --sort top --time week --limit 5
```

You'll see:
```
================================================================================
Downloading r/python
================================================================================

📥 Fetching r/python (top, limit=5)...
✓ Fetched 5 posts from r/python
[1/5] Amazing Python Tutorial...
  ✓ Saved text post: 1abc123_Amazing_Python_Tutorial.md
[2/5] Cool Project...
  ✓ Downloaded media: 1def456_Cool_Project.png
...

✓ Downloaded 5/5 posts from r/python
📁 Saved to: reddit_downloads/r_python
```

Check the `reddit_downloads/r_python/` folder to see your downloads! 📁

## 📚 Common Commands

### Download from Subreddit
```bash
# Top posts this week
python reddit_scraper.py --subreddit AskReddit --sort top --time week --limit 25

# Hot posts (trending now)
python reddit_scraper.py --subreddit pics --sort hot --limit 50

# New posts (latest)
python reddit_scraper.py --subreddit news --sort new --limit 20
```

### Download from User
```bash
python reddit_scraper.py --user username --limit 10
```

### Download Specific Post
```bash
python reddit_scraper.py --url "https://reddit.com/r/pics/comments/abc123/"
```

### Fast Mode (Skip Comments)
```bash
python reddit_scraper.py --subreddit pics --limit 50 --no-comments
```

## 🎯 What Gets Downloaded?

- **Text posts** → `.md` files (Markdown with comments)
- **Images** → `.jpg`, `.png` files
- **Videos** → `.mp4` files
- **Links** → `.html` files (auto-redirect)

Everything is saved to `reddit_downloads/` organized by subreddit!

## 🔧 All Options

| Option | What it does | Example |
|--------|-------------|---------|
| `--subreddit` | Which subreddit | `--subreddit python` |
| `--user` | Which user | `--user spez` |
| `--url` | Specific post URL | `--url "https://..."` |
| `--sort` | How to sort | `--sort top` |
| `--time` | Time period | `--time week` |
| `--limit` | How many posts | `--limit 50` |
| `--output` | Where to save | `--output my_folder` |
| `--no-comments` | Skip comments | `--no-comments` |

### Sort Options
- `hot` - Trending now
- `new` - Latest posts
- `top` - Most upvoted
- `rising` - Rising posts
- `controversial` - Most controversial

### Time Options (for `top` and `controversial`)
- `hour` - Last hour
- `day` - Last 24 hours
- `week` - Last 7 days
- `month` - Last 30 days
- `year` - Last year
- `all` - All time

## 💡 Pro Tips

**Tip 1:** Start small with `--limit 5` to test

**Tip 2:** Use `--no-comments` for faster image/video downloads

**Tip 3:** Check the output folder structure:
```
reddit_downloads/
└── r_python/
    ├── 1abc123_Post_Title.md
    ├── 1def456_Image.jpg
    └── 1ghi789_Video.mp4
```

**Tip 4:** The scraper automatically waits between requests (no need to worry about rate limits!)

## 🐛 Troubleshooting

**"No module named 'requests'"**
```bash
pip install requests
```

**"No items returned"**
- Check if the subreddit name is correct
- Try a different subreddit (e.g., `python`, `pics`, `AskReddit`)

**Need more help?**
- Read the full [README.md](README.md)
- Check [examples.py](examples.py)

## 🎓 Next Steps

1. ✅ Try downloading from your favorite subreddit
2. ✅ Experiment with different sort options
3. ✅ Check out [examples.py](examples.py) for advanced usage
4. ✅ Read the full [README.md](README.md) for all features

---

**Happy scraping!** 🚀

Questions? Open an issue on GitHub!

