# FeedKit

> RSS/Atom feed collection with 449 curated feeds. Python MCP server included.

```python
from feedkit import search_catalog, fetch_feed, FeedStore

# Search the built-in catalog
feeds = search_catalog("cloudflare")

# Fetch a feed
entries = await fetch_feed("https://blog.cloudflare.com/rss/")
for entry in entries:
    print(entry.title, entry.url)

# Subscribe and collect
store = FeedStore()
store.subscribe("https://blog.cloudflare.com/rss/", category="tech")
result = await collect(store)  # async parallel fetch
print(f"{result.new_articles} new articles")
```

## Features

- **449 curated feeds** — tech blogs, academic, government, news, fact-check. All verified with 778K+ articles collected.
- **Async parallel collection** — fetch hundreds of feeds in under a minute
- **SQLite + FTS5** — local storage with full-text search, no server needed
- **OPML import/export** — interop with Feedly, Inoreader, NetNewsWire
- **MCP server** — 9 tools for Claude Code / MCP clients
- **Feed health monitoring** — track success rates and errors per feed

## Install

```bash
pip install feedkit
```

## CLI

```bash
feedkit search aws                        # search catalog
feedkit search --category technology      # by category
feedkit categories                        # list categories

feedkit subscribe https://example.com/rss # subscribe to a feed
feedkit subscribe-catalog -c technology   # subscribe to entire category
feedkit list                              # list subscriptions

feedkit collect                           # fetch all subscriptions
feedkit latest                            # show latest articles
feedkit find "kubernetes deployment"      # full-text search

feedkit import-opml subs.opml             # import OPML
feedkit export-opml backup.opml           # export OPML
feedkit stats                             # catalog + local stats
```

## MCP Server

```bash
pip install "feedkit[mcp]"
feedkit-mcp  # starts stdio MCP server
```

**9 tools:** fetch_single_feed, search_feed_catalog, catalog_stats, collect_feeds, search_articles, get_latest_articles, subscribe_feed, unsubscribe_feed, list_subscriptions

## Built-in Catalog

449 verified feeds across 5 categories:

| Category | Feeds | Examples |
|----------|-------|---------|
| technology | 68 | AWS, Cloudflare, Stripe, Netflix, Spotify, Meta |
| science | 128 | NASA, PLOS, Harvard, Cambridge, BAIR, arXiv |
| finance | 114 | World Bank, BoC, RBA, financial news |
| society | 126 | JTBC, MBC, international news |
| academia | 13 | Research journals, university blogs |

All feeds verified working — collected 778K+ articles via daily automated collection.

## License

[MIT](LICENSE)

<!-- mcp-name: io.github.ArkNill/feedkit -->
