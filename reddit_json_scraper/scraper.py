import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from .network_utils import create_retry_session
from .resume import should_skip, append_manifest

log = logging.getLogger(__name__)

REDDIT_BASE = "https://www.reddit.com"
DEFAULT_HEADERS = {"Accept": "application/json"}

@dataclass
class Post:
    id: str
    permalink: str
    title: str
    url: Optional[str]
    is_gallery: bool
    media_urls: List[str]
    raw: dict

class Scraper:
    """JSON-endpoint-only scraper. No OAuth, no API keys."""
    def __init__(self, user_agent: str = "reddit-json-scraper/0.0.1"):
        self.session = create_retry_session(user_agent=user_agent)

    def _get_json(self, url: str, timeout: float = 15.0) -> dict:
        resp = self.session.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
        resp.raise_for_status()
        return resp.json()

    def fetch_subreddit(self, name: str, sort: str = "hot", limit: int = 50, rate_delay: float = 2.0) -> List[dict]:
        items: List[dict] = []
        after: Optional[str] = None
        fetched = 0
        while fetched < limit:
            page_size = min(100, limit - fetched)
            url = f"{REDDIT_BASE}/r/{name}/{sort}.json?limit={page_size}" + (f"&after={after}" if after else "")
            data = self._get_json(url)
            children = data.get("data", {}).get("children", [])
            if not children:
                break
            items.extend([c.get("data", {}) for c in children])
            fetched += len(children)
            after = data.get("data", {}).get("after")
            if not after:
                break
            time.sleep(rate_delay)
        return items

    def fetch_user(self, username: str, limit: int = 50, rate_delay: float = 2.0) -> List[dict]:
        items: List[dict] = []
        after: Optional[str] = None
        fetched = 0
        while fetched < limit:
            page_size = min(100, limit - fetched)
            url = f"{REDDIT_BASE}/user/{username}/submitted.json?limit={page_size}" + (f"&after={after}" if after else "")
            data = self._get_json(url)
            children = data.get("data", {}).get("children", [])
            if not children:
                break
            items.extend([c.get("data", {}) for c in children])
            fetched += len(children)
            after = data.get("data", {}).get("after")
            if not after:
                break
            time.sleep(rate_delay)
        return items

    def fetch_link(self, url: str) -> dict:
        if not url.endswith(".json"):
            if urlparse(url).path.endswith("/"):
                url = url[:-1]
            url = url + ".json"
        data = self._get_json(url)
        post = data[0]["data"]["children"][0]["data"]
        return post

    def _extract_media(self, post: dict) -> List[str]:
        urls: List[str] = []
        for k in ("url_overridden_by_dest", "url"):
            u = post.get(k)
            if isinstance(u, str) and u.startswith(("http://", "https://")):
                urls.append(u)
                break
        if post.get("is_gallery") and "media_metadata" in post:
            for meta in post["media_metadata"].values():
                if "s" in meta and "u" in meta["s"]:
                    u = meta["s"]["u"].replace("&amp;", "&")
                    urls.append(u)
        return list(dict.fromkeys(urls))

    def normalize(self, post: dict):
        return Post(
            id=post.get("id"),
            permalink=urljoin(REDDIT_BASE, post.get("permalink", "")),
            title=post.get("title", ""),
            url=post.get("url"),
            is_gallery=bool(post.get("is_gallery")),
            media_urls=self._extract_media(post),
            raw=post,
        )

    def write_posts(self, posts: List[dict], out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        normalized = [self.normalize(p) for p in posts]
        out_path = out_dir / "posts.jsonl"
        with out_path.open("a", encoding="utf-8") as f:
            for p in normalized:
                f.write(json.dumps({"id": p.id, "permalink": p.permalink, "title": p.title,
                                    "url": p.url, "is_gallery": p.is_gallery,
                                    "media_urls": p.media_urls, "raw": p.raw}) + "\n")
        log.info("Wrote %d posts to %s", len(normalized), out_path)

    def _download_one(self, url: str, out_path: Path, expected_size: Optional[int] = None, resume: bool = False):
        if resume and should_skip(str(out_path), expected_size):
            return "skipped"
        tmp = out_path.with_suffix(out_path.suffix + ".part")
        with self.session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with tmp.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    if chunk:
                        f.write(chunk)
        os.replace(tmp, out_path)
        return "ok"

    def _derive_filename(self, url: str) -> str:
        return os.path.basename(urlparse(url).path) or "media"

    def download_media(self, posts: List[dict], out_dir: Path, resume: bool = False) -> None:
        out_media = out_dir / "media"
        successes = 0
        normalized = [self.normalize(p) for p in posts]
        for p in normalized:
            for mu in p.media_urls:
                fname = self._derive_filename(mu)
                status = self._download_one(mu, out_media / p.id / fname, resume=resume)
                append_manifest(str(out_media / p.id), {"url": mu, "file": fname, "status": status})
                successes += int(status == "ok")
        log.info("Downloaded %d media files", successes)

    async def download_media_async(self, posts: List[dict], out_dir: Path, resume: bool = False) -> None:
        try:
            from .async_download import download_many
        except Exception as e:
            log.error("Async dependencies not available: %s", e)
            self.download_media(posts, out_dir, resume=resume)
            return
        out_media = out_dir / "media"
        pairs = []
        normalized = [self.normalize(p) for p in posts]
        for p in normalized:
            for mu in p.media_urls:
                fname = self._derive_filename(mu)
                target = out_media / p.id / fname
                if resume and should_skip(str(target)):
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                pairs.append((mu, str(target)))
        if not pairs:
            log.info("No media to download (after resume check).")
            return
        results = await download_many(pairs, concurrency=6)
        for (mu, path), res in zip(pairs, results):
            status = "ok" if not isinstance(res, Exception) else f"error:{res}"
            append_manifest(str(Path(path).parent), {"url": mu, "file": os.path.basename(path), "status": status})
        log.info("Async download complete: %d items", len(pairs))
