"""Tests for storage.py — SQLite subscription and article store."""

import tempfile
from pathlib import Path

import pytest

from feedkit.storage import Article, FeedStore, Subscription


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as td:
        s = FeedStore(db_path=Path(td) / "test.db")
        yield s
        s.close()


# === Subscriptions ===


def test_subscribe(store):
    store.subscribe("https://example.com/rss", title="Example", category="tech")
    subs = store.list_subscriptions()
    assert len(subs) == 1
    assert subs[0].feed_url == "https://example.com/rss"
    assert subs[0].title == "Example"
    assert subs[0].category == "tech"


def test_subscribe_duplicate(store):
    store.subscribe("https://example.com/rss")
    store.subscribe("https://example.com/rss")  # should not raise
    assert store.subscription_count() == 1


def test_unsubscribe(store):
    store.subscribe("https://example.com/rss")
    store.unsubscribe("https://example.com/rss")
    assert store.subscription_count() == 0


def test_subscription_count(store):
    store.subscribe("https://a.com/rss")
    store.subscribe("https://b.com/rss")
    store.subscribe("https://c.com/rss")
    assert store.subscription_count() == 3


def test_list_subscriptions_sorted(store):
    store.subscribe("https://z.com/rss", category="z", title="Z Feed")
    store.subscribe("https://a.com/rss", category="a", title="A Feed")
    subs = store.list_subscriptions()
    assert subs[0].category == "a"


# === Articles ===


def test_save_articles(store):
    store.subscribe("https://example.com/rss")
    articles = [
        Article(guid="1", feed_url="https://example.com/rss", title="First", url="https://example.com/1"),
        Article(guid="2", feed_url="https://example.com/rss", title="Second", url="https://example.com/2"),
    ]
    new = store.save_articles(articles)
    assert new == 2
    assert store.article_count() == 2


def test_save_articles_dedup(store):
    store.subscribe("https://example.com/rss")
    articles = [Article(guid="1", feed_url="https://example.com/rss", title="First")]
    store.save_articles(articles)
    new = store.save_articles(articles)  # duplicate
    assert new == 0
    assert store.article_count() == 1


def test_get_latest(store):
    store.subscribe("https://example.com/rss")
    articles = [
        Article(guid=str(i), feed_url="https://example.com/rss", title=f"Article {i}")
        for i in range(10)
    ]
    store.save_articles(articles)
    latest = store.get_latest(count=5)
    assert len(latest) == 5


def test_get_latest_by_category(store):
    store.subscribe("https://a.com/rss", category="tech")
    store.subscribe("https://b.com/rss", category="science")
    store.save_articles([
        Article(guid="1", feed_url="https://a.com/rss", title="Tech article"),
        Article(guid="2", feed_url="https://b.com/rss", title="Science article"),
    ])
    tech = store.get_latest(category="tech")
    assert len(tech) == 1
    assert tech[0].title == "Tech article"


# === FTS Search ===


def test_search_fts(store):
    store.subscribe("https://example.com/rss")
    store.save_articles([
        Article(guid="1", feed_url="https://example.com/rss", title="Kubernetes deployment guide", summary="How to deploy pods"),
        Article(guid="2", feed_url="https://example.com/rss", title="Python async tutorial", summary="Using asyncio"),
    ])
    results = store.search("kubernetes")
    assert len(results) == 1
    assert "Kubernetes" in results[0].title


def test_search_no_match(store):
    store.subscribe("https://example.com/rss")
    store.save_articles([
        Article(guid="1", feed_url="https://example.com/rss", title="Hello world"),
    ])
    results = store.search("zzzznonexistent")
    assert len(results) == 0


# === Health ===


def test_update_fetch_status_success(store):
    store.subscribe("https://example.com/rss")
    store.update_fetch_status("https://example.com/rss", success=True)
    subs = store.list_subscriptions()
    assert subs[0].fetch_count == 1
    assert subs[0].last_fetch is not None


def test_update_fetch_status_error(store):
    store.subscribe("https://example.com/rss")
    store.update_fetch_status("https://example.com/rss", success=False, error="timeout")
    subs = store.list_subscriptions()
    assert subs[0].error_count == 1
    assert subs[0].last_error == "timeout"


def test_get_health(store):
    store.subscribe("https://example.com/rss")
    health = store.get_health()
    assert len(health) == 1
    assert health[0]["feed_url"] == "https://example.com/rss"
