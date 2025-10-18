# 🎯 Interactive Mode Guide

The easiest way to use Reddit JSON Scraper!

## 🚀 Quick Start

```bash
python interactive.py
```

That's it! The script will guide you through everything.

---

## 📖 How It Works

### Step 1: Choose What to Scrape

```
📋 What would you like to scrape?

  1. Subreddit - Download posts from a subreddit
  2. User - Download posts from a specific user
  3. Single Post - Download a specific post by URL

Choose an option (1/2/3):
```

**Just type the number and press Enter.**

---

## 🔄 Example Workflows

### Example 1: Download from a Subreddit

```
Choose an option (1/2/3): 1

💡 Enter the subreddit name (without 'r/')
   Examples: python, pics, AskReddit, funny
Subreddit name: python

📊 How should posts be sorted?

  hot - Trending posts (default)
  new - Latest posts
  top - Most upvoted posts
  rising - Rising posts
  controversial - Most controversial posts

Sort by [hot]: top

⏰ Time period for filtering:

  hour - Last hour
  day - Last 24 hours
  week - Last 7 days (default)
  month - Last 30 days
  year - Last year
  all - All time

Time period [week]: week

🔢 How many posts to download?
   Recommended: 5-50 posts
   Maximum: 1000 posts
Number of posts [25]: 10

📝 Download comments with posts? (yes/no) [yes]: yes

📁 Use custom output directory? (yes/no) [yes]: no

----------------------------------------------------------------------
📋 DOWNLOAD SUMMARY
----------------------------------------------------------------------
  Subreddit: r/python
  Sort: top
  Time: week
  Limit: 10 posts
  Comments: Yes
  Output: reddit_downloads
----------------------------------------------------------------------

🚀 Start download? (yes/no) [yes]: yes
```

**Result:** Downloads 10 top posts from r/python this week with comments!

---

### Example 2: Download from a User

```
Choose an option (1/2/3): 2

💡 Enter the Reddit username (without 'u/')
   Examples: spez, AutoModerator
Username: spez

📊 How should posts be sorted?

  new - Latest posts (default)
  hot - Trending posts
  top - Most upvoted posts
  controversial - Most controversial posts

Sort by [new]: new

🔢 How many posts to download?
   Recommended: 5-50 posts
Number of posts [25]: 15

📝 Download comments with posts? (yes/no) [yes]: no

----------------------------------------------------------------------
📋 DOWNLOAD SUMMARY
----------------------------------------------------------------------
  User: u/spez
  Sort: new
  Limit: 15 posts
  Comments: No
  Output: reddit_downloads
----------------------------------------------------------------------

🚀 Start download? (yes/no) [yes]: yes
```

**Result:** Downloads 15 latest posts from u/spez without comments!

---

### Example 3: Download a Single Post

```
Choose an option (1/2/3): 3

💡 Enter the Reddit post URL
   Examples:
   - https://reddit.com/r/pics/comments/abc123/
   - https://www.reddit.com/r/AskReddit/comments/xyz789/what_is/

Post URL: https://reddit.com/r/nextfuckinglevel/comments/1o8ze9o/

📝 Download comments with the post? (yes/no) [yes]: yes

----------------------------------------------------------------------
📋 DOWNLOAD SUMMARY
----------------------------------------------------------------------
  URL: https://reddit.com/r/nextfuckinglevel/comments/1o8ze9o/
  Comments: Yes
  Output: reddit_downloads
----------------------------------------------------------------------

🚀 Start download? (yes/no) [yes]: yes
```

**Result:** Downloads that specific post with all comments!

---

## 💡 Tips & Tricks

### Default Values

When you see `[default]` in brackets, you can just press **Enter** to use that value:

```
Sort by [hot]:  ← Just press Enter to use "hot"
```

### Canceling

Press **Ctrl+C** at any time to cancel:

```
^C
❌ Cancelled by user.
```

### Saying No to Download

If you don't like the summary, say "no":

```
🚀 Start download? (yes/no) [yes]: no

❌ Download cancelled.
```

The script will exit without downloading anything.

### Quick Answers

You can use shortcuts:
- `y` instead of `yes`
- `n` instead of `no`

```
Download comments? (yes/no) [yes]: y  ← Same as "yes"
```

---

## 🎯 Common Use Cases

### Archive Your Favorite Subreddit

```
Option: 1 (Subreddit)
Subreddit: AskReddit
Sort: top
Time: month
Limit: 100
Comments: yes
```

### Monitor New Posts

```
Option: 1 (Subreddit)
Subreddit: news
Sort: new
Limit: 25
Comments: no  ← Faster without comments
```

### Download a Collection of Images

```
Option: 1 (Subreddit)
Subreddit: pics
Sort: hot
Limit: 50
Comments: no  ← Don't need comments for images
```

### Save an Interesting Post

```
Option: 3 (Single Post)
URL: [paste the URL]
Comments: yes
```

---

## 🔧 Troubleshooting

### "No such file or directory"

Make sure you're in the right directory:

```bash
cd reddit-json-scraper
python interactive.py
```

### "No module named 'reddit_scraper'"

The `interactive.py` script needs to be in the same folder as `reddit_scraper.py`.

Check with:
```bash
ls -la
# You should see both files
```

### "ModuleNotFoundError: No module named 'requests'"

Install dependencies:
```bash
pip install -r requirements.txt
```

Or if using virtual environment:
```bash
source venv/bin/activate  # Activate first!
pip install -r requirements.txt
```

### Script Doesn't Ask Questions

Make sure you're running `interactive.py`, not `reddit_scraper.py`:

```bash
python interactive.py  ← Interactive mode
python reddit_scraper.py --subreddit python  ← Command-line mode
```

---

## 🆚 Interactive vs Command-Line

### Use Interactive Mode When:
- ✅ You're new to the tool
- ✅ You want guidance
- ✅ You don't remember the options
- ✅ You want to see a summary before downloading

### Use Command-Line Mode When:
- ✅ You know exactly what you want
- ✅ You're scripting/automating
- ✅ You want to save time on repeated tasks
- ✅ You're comfortable with command-line arguments

**Both modes do the same thing!** Choose what's comfortable for you.

---

## 📚 Next Steps

After using interactive mode a few times, you might want to try:

1. **Command-line mode** for faster downloads
2. **Python API** for custom scripts
3. **Automation** with cron jobs or scheduled tasks

See the main [README.md](README.md) for advanced usage!

---

## 🎉 Examples

### Minimal Input (Use All Defaults)

```
Choose: 1
Subreddit: python
Sort: [Enter]  ← Use default "hot"
Limit: [Enter]  ← Use default "25"
Comments: [Enter]  ← Use default "yes"
Custom dir: [Enter]  ← Use default "no"
Start: [Enter]  ← Use default "yes"
```

**Done in 6 key presses!** (Plus typing "python")

### Maximum Control

```
Choose: 1
Subreddit: AskReddit
Sort: top
Time: month
Limit: 100
Comments: yes
Custom dir: yes
Directory: my_askreddit_archive
Start: yes
```

**Full control over everything!**

---

**Happy scraping!** 🚀

For more help, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [INSTALL.md](INSTALL.md) - Installation help

