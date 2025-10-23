import argparse
import asyncio
import logging
from pathlib import Path
from .logconfig import configure_logging
from .scraper import Scraper

def build_parser():
    p = argparse.ArgumentParser(
        prog="reddit-json-scraper",
        description="Download Reddit posts, comments, and media via public .json endpoints",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("subreddit", help="Scrape a subreddit by sort and limit")
    sp.add_argument("name", help="Subreddit name, e.g., 'python' (without r/)")
    sp.add_argument("--sort", choices=["hot","new","top","rising"], default="hot")
    sp.add_argument("--limit", type=int, default=50)
    sp.add_argument("--out", type=Path, default=Path("out"))
    sp.add_argument("--media", action="store_true")
    sp.add_argument("--resume", action="store_true")
    sp.add_argument("--fast", action="store_true")
    sp.add_argument("--rate-delay", type=float, default=2.0)
    sp.add_argument("--debug", action="store_true")

    up = sub.add_parser("user", help="Scrape a user's posts")
    up.add_argument("username")
    up.add_argument("--limit", type=int, default=50)
    up.add_argument("--out", type=Path, default=Path("out"))
    up.add_argument("--media", action="store_true")
    up.add_argument("--resume", action="store_true")
    up.add_argument("--fast", action="store_true")
    up.add_argument("--rate-delay", type=float, default=2.0)
    up.add_argument("--debug", action="store_true")

    lp = sub.add_parser("link", help="Scrape a single post by URL (add .json)")
    lp.add_argument("url", help="Full reddit post URL")
    lp.add_argument("--out", type=Path, default=Path("out"))
    lp.add_argument("--media", action="store_true")
    lp.add_argument("--resume", action="store_true")
    lp.add_argument("--fast", action="store_true")
    lp.add_argument("--debug", action="store_true")

    return p

def main():
    args = build_parser().parse_args()
    configure_logging(debug=args.debug if hasattr(args, "debug") else False)
    log = logging.getLogger("cli")
    s = Scraper()

    if args.cmd == "subreddit":
        log.info("Scraping subreddit r/%s sort=%s limit=%s", args.name, args.sort, args.limit)
        posts = s.fetch_subreddit(args.name, sort=args.sort, limit=args.limit, rate_delay=args.rate_delay)
        s.write_posts(posts, args.out)
        if args.media:
            if args.fast:
                asyncio.run(s.download_media_async(posts, args.out, resume=args.resume))
            else:
                s.download_media(posts, args.out, resume=args.resume)
    elif args.cmd == "user":
        log.info("Scraping user u/%s limit=%s", args.username, args.limit)
        posts = s.fetch_user(args.username, limit=args.limit, rate_delay=args.rate_delay)
        s.write_posts(posts, args.out)
        if args.media:
            if args.fast:
                asyncio.run(s.download_media_async(posts, args.out, resume=args.resume))
            else:
                s.download_media(posts, args.out, resume=args.resume)
    elif args.cmd == "link":
        log.info("Scraping link %s", args.url)
        post = s.fetch_link(args.url)
        s.write_posts([post], args.out)
        if args.media:
            if args.fast:
                asyncio.run(s.download_media_async([post], args.out, resume=args.resume))
            else:
                s.download_media([post], args.out, resume=args.resume)

if __name__ == "__main__":
    main()
