# 📦 Installation Guide

Complete installation instructions for all platforms and scenarios.

## 🚀 Quick Install (Recommended)

### For Most Users (Virtual Environment)

This is the **recommended** method that works on all systems:

```bash
# 1. Clone the repository
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the scraper
python reddit_scraper.py --subreddit python --limit 5
```

**That's it!** ✅

---

## 🐧 Linux/Ubuntu/Debian Installation

### Method 1: Virtual Environment (Recommended)

Modern Linux distributions (Ubuntu 23.04+, Debian 12+) require virtual environments:

```bash
# Clone the repository
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python reddit_scraper.py --subreddit python --limit 5
```

**To use later:**
```bash
cd reddit-json-scraper
source venv/bin/activate  # Activate the venv
python reddit_scraper.py --subreddit pics --limit 10
```

**To deactivate:**
```bash
deactivate
```

### Method 2: System-Wide (Not Recommended)

If you really need system-wide installation:

```bash
# Option A: Use apt (if available)
sudo apt install python3-requests

# Option B: Override protection (not recommended)
pip install requests --break-system-packages
```

⚠️ **Warning:** System-wide installation can break your Python environment. Use virtual environments instead!

### Method 3: Using pipx (For Tool Installation)

```bash
# Install pipx if not installed
sudo apt install pipx

# This won't work directly for this tool, but good for future reference
# For now, use Method 1 (virtual environment)
```

---

## 🍎 macOS Installation

### Using Virtual Environment (Recommended)

```bash
# Clone the repository
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python reddit_scraper.py --subreddit python --limit 5
```

### Using Homebrew Python

If you have Python from Homebrew:

```bash
# Install Python (if needed)
brew install python

# Clone and install
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# Install dependencies
pip3 install -r requirements.txt

# Run the scraper
python3 reddit_scraper.py --subreddit python --limit 5
```

---

## 🪟 Windows Installation

### Method 1: Virtual Environment (Recommended)

```cmd
# Clone the repository
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python reddit_scraper.py --subreddit python --limit 5
```

### Method 2: Direct Installation

```cmd
# Clone the repository
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# Install dependencies
pip install requests

# Run the scraper
python reddit_scraper.py --subreddit python --limit 5
```

### Using PowerShell

If activation fails in PowerShell:

```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate normally
venv\Scripts\Activate.ps1
```

---

## 🐳 Docker Installation (Advanced)

For isolated, reproducible environments:

```bash
# Clone the repository
git clone https://github.com/0anxt/reddit-json-scraper.git
cd reddit-json-scraper

# Create Dockerfile (see below)
# Build the image
docker build -t reddit-scraper .

# Run the scraper
docker run -v $(pwd)/downloads:/app/reddit_downloads reddit-scraper \
  --subreddit python --limit 5
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reddit_scraper.py .

ENTRYPOINT ["python", "reddit_scraper.py"]
```

---

## 🔧 Troubleshooting

### "externally-managed-environment" Error

**Problem:** Modern Linux systems prevent system-wide pip installations.

**Solution:** Use a virtual environment (see Linux Method 1 above).

**Why this happens:** PEP 668 protects your system Python from conflicts.

### "python: command not found"

**Solution:**
```bash
# Try python3 instead
python3 --version

# Or install Python
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-venv python3-pip

# macOS:
brew install python

# Windows: Download from python.org
```

### "No module named 'venv'"

**Solution:**
```bash
# Ubuntu/Debian:
sudo apt install python3-venv

# Or use python3-full:
sudo apt install python3-full
```

### "pip: command not found"

**Solution:**
```bash
# Ubuntu/Debian:
sudo apt install python3-pip

# macOS:
python3 -m ensurepip

# Or use:
python3 -m pip install requests
```

### Virtual Environment Won't Activate

**Linux/Mac:**
```bash
# Make sure you're using source, not sh
source venv/bin/activate

# Not: sh venv/bin/activate
```

**Windows:**
```cmd
# Use the full path
venv\Scripts\activate.bat

# Or in PowerShell:
venv\Scripts\Activate.ps1
```

### "Permission denied" on Linux

**Solution:**
```bash
# Don't use sudo with pip in venv
# Just activate venv first, then:
pip install -r requirements.txt

# If you need to fix permissions:
sudo chown -R $USER:$USER venv/
```

---

## 📋 Installation Checklist

- [ ] Python 3.7+ installed (`python3 --version`)
- [ ] Git installed (`git --version`)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Test run successful

---

## 🎯 Quick Reference

### Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Scraper

```bash
python reddit_scraper.py --subreddit python --limit 5
```

---

## 🌐 Installing Without Git

If you don't have Git:

1. **Download ZIP:**
   - Go to https://github.com/0anxt/reddit-json-scraper
   - Click "Code" → "Download ZIP"
   - Extract the ZIP file

2. **Navigate to folder:**
   ```bash
   cd reddit-json-scraper-main
   ```

3. **Follow installation steps above** (create venv, install dependencies)

---

## 🔄 Updating the Scraper

To get the latest version:

```bash
# Navigate to repository
cd reddit-json-scraper

# Deactivate venv if active
deactivate

# Pull latest changes
git pull

# Reactivate venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Update dependencies (if changed)
pip install -r requirements.txt
```

---

## 🚀 One-Line Install Scripts

### Linux/Mac

```bash
git clone https://github.com/0anxt/reddit-json-scraper.git && cd reddit-json-scraper && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && echo "✅ Installation complete! Run: python reddit_scraper.py --subreddit python --limit 5"
```

### Windows (PowerShell)

```powershell
git clone https://github.com/0anxt/reddit-json-scraper.git; cd reddit-json-scraper; python -m venv venv; venv\Scripts\Activate.ps1; pip install -r requirements.txt; Write-Host "✅ Installation complete! Run: python reddit_scraper.py --subreddit python --limit 5"
```

---

## 📚 Additional Resources

- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html
- **PEP 668 (externally-managed):** https://peps.python.org/pep-0668/
- **pip Documentation:** https://pip.pypa.io/
- **Git Installation:** https://git-scm.com/downloads

---

## 💡 Best Practices

1. ✅ **Always use virtual environments** - Keeps your system clean
2. ✅ **Activate venv before running** - Ensures correct dependencies
3. ✅ **Don't use sudo with pip** - Can break your system
4. ✅ **Update regularly** - `git pull` to get latest features
5. ✅ **Deactivate when done** - `deactivate` to exit venv

---

## 🆘 Still Having Issues?

1. **Check Python version:** `python3 --version` (need 3.7+)
2. **Check pip version:** `pip --version`
3. **Try the virtual environment method** (works 99% of the time)
4. **Open an issue:** https://github.com/0anxt/reddit-json-scraper/issues

Include in your issue:
- Operating system and version
- Python version
- Full error message
- Steps you tried

---

**Happy scraping!** 🚀

