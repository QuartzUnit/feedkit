"""Tests for opml.py — OPML import/export."""

import tempfile
from pathlib import Path

import pytest

from feedkit.opml import export_opml, import_opml
from feedkit.storage import FeedStore


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as td:
        s = FeedStore(db_path=Path(td) / "test.db")
        yield s
        s.close()


@pytest.fixture
def sample_opml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>Test</title></head>
  <body>
    <outline text="Tech">
      <outline type="rss" text="Cloudflare Blog" xmlUrl="https://blog.cloudflare.com/rss/" />
      <outline type="rss" text="AWS Blog" xmlUrl="https://aws.amazon.com/blogs/aws/feed/" />
    </outline>
    <outline text="Science">
      <outline type="rss" text="NASA" xmlUrl="https://www.nasa.gov/rss/dyn/breaking_news.rss" />
    </outline>
  </body>
</opml>"""
    path = tmp_path / "test.opml"
    path.write_text(content, encoding="utf-8")
    return path


def test_import_opml(store, sample_opml):
    count = import_opml(store, sample_opml)
    assert count == 3
    subs = store.list_subscriptions()
    assert len(subs) == 3


def test_import_opml_categories(store, sample_opml):
    import_opml(store, sample_opml)
    subs = store.list_subscriptions()
    categories = {s.category for s in subs}
    assert "Tech" in categories
    assert "Science" in categories


def test_export_opml(store, tmp_path):
    store.subscribe("https://blog.cloudflare.com/rss/", title="Cloudflare", category="tech")
    store.subscribe("https://www.nasa.gov/rss/feed", title="NASA", category="science")

    path = tmp_path / "export.opml"
    count = export_opml(store, path)
    assert count == 2
    assert path.exists()

    content = path.read_text(encoding="utf-8")
    assert "cloudflare" in content.lower()
    assert "nasa" in content.lower()
    assert 'version="2.0"' in content


def test_roundtrip(store, tmp_path):
    """Import → export → import should preserve feeds."""
    store.subscribe("https://a.com/rss", title="Feed A", category="cat1")
    store.subscribe("https://b.com/rss", title="Feed B", category="cat2")

    path = tmp_path / "roundtrip.opml"
    export_opml(store, path)

    # New store
    store2 = FeedStore(db_path=tmp_path / "test2.db")
    import_opml(store2, path)
    subs = store2.list_subscriptions()
    assert len(subs) == 2
    urls = {s.feed_url for s in subs}
    assert "https://a.com/rss" in urls
    assert "https://b.com/rss" in urls
    store2.close()
