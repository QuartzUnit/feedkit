"""FeedKit MCP server — RSS feed tools for Claude Code."""

import asyncio
import json

from fastmcp import FastMCP

from feedkit.catalog import get_catalog_stats, search_catalog
from feedkit.core import collect, fetch_feed
from feedkit.storage import FeedStore

mcp = FastMCP(
    "feedkit",
    instructions="RSS/Atom feed collection with 444 curated feeds. Search, subscribe, collect, and search articles.",
)

_store: FeedStore | None = None


def _get_store() -> FeedStore:
    global _store
    if _store is None:
        _store = FeedStore()
    return _store


@mcp.tool()
async def fetch_single_feed(url: str, count: int = 10) -> str:
    """Fetch latest entries from a single RSS/Atom feed URL.

    Returns the most recent articles with title, URL, summary, and date.
    No subscription needed — just provide any RSS feed URL.

    Args:
        url: RSS or Atom feed URL.
        count: Maximum entries to return (default: 10).
    """
    entries = await fetch_feed(url, count=count)
    return json.dumps(
        [{"title": e.title, "url": e.url, "summary": e.summary[:200], "published": e.published, "author": e.author}
         for e in entries],
        ensure_ascii=False,
    )


@mcp.tool()
def search_feed_catalog(query: str = "", category: str = "", language: str = "", count: int = 20) -> str:
    """Search the built-in catalog of 444 curated RSS feeds.

    The catalog includes tech blogs (AWS, Cloudflare, Netflix...),
    academic journals, government sources, news outlets, and more.
    All feeds are verified working with 778K+ articles collected.

    Args:
        query: Search by title or domain (e.g., "aws", "cloudflare", "nasa").
        category: Filter by category: technology, science, finance, society, academia.
        language: Filter by language code (e.g., "en", "ko").
        count: Maximum results (default: 20).
    """
    feeds = search_catalog(query, category=category, language=language, limit=count)
    return json.dumps(
        [{"url": f.url, "title": f.title, "category": f.category, "language": f.language, "domain": f.domain}
         for f in feeds],
        ensure_ascii=False,
    )


@mcp.tool()
def catalog_stats() -> str:
    """Get statistics about the built-in feed catalog."""
    return json.dumps(get_catalog_stats(), ensure_ascii=False)


@mcp.tool()
async def collect_feeds(category: str = "") -> str:
    """Collect new articles from all subscribed feeds.

    Fetches all subscriptions in parallel and stores new articles.
    Use search_feed_catalog to find feeds, then subscribe before collecting.

    Args:
        category: Only collect from this category (empty = all).
    """
    store = _get_store()
    result = await collect(store, category=category)
    return json.dumps({
        "feeds_total": result.feeds_total,
        "feeds_ok": result.feeds_ok,
        "feeds_error": result.feeds_error,
        "new_articles": result.new_articles,
        "duration_ms": round(result.duration_ms, 1),
    }, ensure_ascii=False)


@mcp.tool()
def search_articles(query: str, count: int = 10) -> str:
    """Full-text search across all collected articles.

    Searches titles, summaries, and authors using SQLite FTS5.
    Articles must be collected first with collect_feeds.

    Args:
        query: Search query.
        count: Maximum results (default: 10).
    """
    store = _get_store()
    articles = store.search(query, count=count)
    return json.dumps(
        [{"title": a.title, "url": a.url, "summary": a.summary[:200], "published": a.published}
         for a in articles],
        ensure_ascii=False,
    )


@mcp.tool()
def get_latest_articles(category: str = "", count: int = 20) -> str:
    """Get the most recently collected articles.

    Args:
        category: Filter by subscription category (empty = all).
        count: Number of articles (default: 20).
    """
    store = _get_store()
    articles = store.get_latest(count=count, category=category)
    return json.dumps(
        [{"title": a.title, "url": a.url, "summary": a.summary[:200], "published": a.published, "feed_url": a.feed_url}
         for a in articles],
        ensure_ascii=False,
    )


@mcp.tool()
def subscribe_feed(url: str, title: str = "", category: str = "") -> str:
    """Subscribe to an RSS feed for ongoing collection.

    Args:
        url: RSS/Atom feed URL.
        title: Display title (optional).
        category: Category label (optional).
    """
    store = _get_store()
    store.subscribe(url, title=title, category=category)
    return json.dumps({"status": "subscribed", "url": url})


@mcp.tool()
def unsubscribe_feed(url: str) -> str:
    """Unsubscribe from a feed.

    Args:
        url: Feed URL to unsubscribe.
    """
    store = _get_store()
    store.unsubscribe(url)
    return json.dumps({"status": "unsubscribed", "url": url})


@mcp.tool()
def list_subscriptions() -> str:
    """List all current feed subscriptions with their status."""
    store = _get_store()
    subs = store.list_subscriptions()
    return json.dumps(
        [{"url": s.feed_url, "title": s.title, "category": s.category, "fetch_count": s.fetch_count,
          "error_count": s.error_count, "last_fetch": s.last_fetch}
         for s in subs],
        ensure_ascii=False,
    )


def main():
    """Run the MCP server (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
