def test_normalize_structure():
    from reddit_json_scraper.scraper import Scraper
    s = Scraper()
    fake = {
        "id": "abc",
        "permalink": "/r/test/comments/abc/title/",
        "title": "hello",
        "url": "https://i.redd.it/xyz.png",
        "is_gallery": False,
    }
    p = s.normalize(fake)
    assert p.id == "abc"
    assert p.title == "hello"
    assert p.permalink.endswith("/r/test/comments/abc/title/")
    assert "i.redd.it" in p.media_urls[0]
