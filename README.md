# FeedKit

[![PyPI](https://img.shields.io/pypi/v/feedkit)](https://pypi.org/project/feedkit/)
[![Python](https://img.shields.io/pypi/pyversions/feedkit)](https://pypi.org/project/feedkit/)
[![License](https://img.shields.io/github/license/QuartzUnit/feedkit)](https://github.com/QuartzUnit/feedkit/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen)]()

> RSS/Atom feed collection with **444 curated, verified feeds**. CLI + Python API + MCP server.

## Quick Start

```bash
pip install feedkit

feedkit search cloudflare           # search the built-in catalog
feedkit subscribe-catalog -c technology   # subscribe to all 68 tech feeds
feedkit collect                     # fetch all subscriptions (async parallel)
feedkit find "kubernetes"           # full-text search collected articles
```

## Install

```bash
pip install feedkit             # core (CLI + Python API)
pip install "feedkit[mcp]"      # + MCP server
pip install "feedkit[all]"      # + MCP + OPML import/export
```

**Requirements:** Python 3.11+

## CLI Reference

### Catalog Commands

#### `feedkit search [QUERY]`

Search the built-in catalog of 444 curated feeds.

```bash
feedkit search aws                    # search by title or domain
feedkit search --category science     # filter by category
feedkit search --language ko          # filter by language
feedkit search -c finance -l en -n 50 # combine filters
feedkit search -j                     # JSON output (for piping)
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--category` | `-c` | | Filter by category |
| `--language` | `-l` | | Filter by language code (`en`, `ko`, `ja`, `zh`) |
| `--limit` | `-n` | 20 | Max results |
| `--json-output` | `-j` | | Output as JSON |

#### `feedkit categories`

List all available catalog categories.

```
$ feedkit categories
  academia
  finance
  pets
  science
  society
  technology
```

#### `feedkit stats`

Show catalog and local subscription statistics.

```
$ feedkit stats
Catalog: 444 feeds
  academia: 13
  finance: 89
  pets: 27
  science: 128
  society: 119
  technology: 68

Local: 68 subscriptions, 1,247 articles
```

### Subscription Commands

#### `feedkit subscribe <URL>`

Subscribe to a single feed.

```bash
feedkit subscribe https://blog.cloudflare.com/rss/
feedkit subscribe https://example.com/rss -c tech -t "My Feed"
```

| Option | Short | Description |
|--------|-------|-------------|
| `--category` | `-c` | Category label |
| `--title` | `-t` | Display title override |

#### `feedkit subscribe-catalog -c <CATEGORY>`

Subscribe to all feeds in a catalog category at once.

```bash
feedkit subscribe-catalog -c technology   # subscribe to all 68 tech feeds
feedkit subscribe-catalog -c science      # subscribe to all 128 science feeds
```

#### `feedkit unsubscribe <URL>`

Remove a feed subscription and its collected articles.

#### `feedkit list`

List all current subscriptions with fetch counts and error counts.

### Collection Commands

#### `feedkit collect`

Fetch new articles from all subscribed feeds (async parallel).

```bash
feedkit collect                    # collect all
feedkit collect -c technology      # collect only tech feeds
feedkit collect -n 50              # max 50 concurrent requests
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--category` | `-c` | | Only collect from this category |
| `--concurrency` | `-n` | 20 | Max concurrent HTTP requests |

Output:
```
Collecting from 68 feeds...
 67/68 feeds OK, 412 new articles, 8234ms
```

#### `feedkit latest`

Show most recently collected articles.

```bash
feedkit latest                # latest 20 articles
feedkit latest -n 50          # latest 50
feedkit latest -c finance     # latest from finance only
```

#### `feedkit find <QUERY>`

Full-text search (SQLite FTS5) across all collected articles.

```bash
feedkit find "kubernetes deployment"
feedkit find "large language model" -n 50
```

### OPML Commands

#### `feedkit import-opml <PATH>`

Import feeds from an OPML file (Feedly, Inoreader, NetNewsWire, etc.).

```bash
feedkit import-opml subscriptions.opml
```

#### `feedkit export-opml <PATH>`

Export current subscriptions to OPML.

```bash
feedkit export-opml backup.opml
```

## Python API

```python
from feedkit import search_catalog, fetch_feed, get_catalog_stats, FeedStore
from feedkit.core import collect

# Search the built-in catalog
feeds = search_catalog("cloudflare")
feeds = search_catalog(category="technology", language="en", limit=50)

# Fetch a single feed (async)
entries = await fetch_feed("https://blog.cloudflare.com/rss/")
for entry in entries:
    print(entry.title, entry.url, entry.published)

# Subscribe and collect
store = FeedStore()                              # SQLite at ~/.feedkit/feedkit.db
store.subscribe("https://blog.cloudflare.com/rss/", category="tech")
result = await collect(store, concurrency=20)    # async parallel fetch
print(f"{result.new_articles} new, {result.feeds_ok}/{result.feeds_total} OK")

# Search collected articles (FTS5)
articles = store.search("kubernetes", count=10)

# Latest articles
articles = store.get_latest(count=20, category="tech")

# Feed health
health = store.get_health()                      # fetch/error counts per feed

# Catalog stats
stats = get_catalog_stats()                      # {total_feeds, categories, languages}

store.close()
```

### Key Classes

| Class | Description |
|-------|-------------|
| `FeedStore` | SQLite-backed subscription + article store (`~/.feedkit/feedkit.db`) |
| `FeedEntry` | Single entry from a fetched feed (title, url, summary, published, author) |
| `CollectResult` | Bulk collection result (feeds_ok, feeds_error, new_articles, duration_ms) |
| `CatalogFeed` | Entry from the built-in catalog (url, title, category, subcategory, language, domain) |

## MCP Server

```bash
pip install "feedkit[mcp]"
feedkit-mcp                    # starts stdio MCP server
```

### Configuration

Claude Code (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "feedkit": {
      "command": "feedkit-mcp"
    }
  }
}
```

### Tools Reference

| # | Tool | Parameters | Description |
|---|------|-----------|-------------|
| 1 | `fetch_single_feed` | `url`, `count=10` | Fetch entries from any RSS/Atom URL (no subscription needed) |
| 2 | `search_feed_catalog` | `query`, `category`, `language`, `count=20` | Search the built-in 444-feed catalog |
| 3 | `catalog_stats` | | Get catalog statistics (total, by category, by language) |
| 4 | `subscribe_feed` | `url`, `title`, `category` | Subscribe to a feed for ongoing collection |
| 5 | `unsubscribe_feed` | `url` | Remove a subscription |
| 6 | `list_subscriptions` | | List all subscriptions with status |
| 7 | `collect_feeds` | `category` | Collect new articles from all subscriptions |
| 8 | `search_articles` | `query`, `count=10` | Full-text search across collected articles |
| 9 | `get_latest_articles` | `category`, `count=20` | Get most recently collected articles |

### MCP Workflow Example

```
User: "What are the latest AI papers on arXiv?"

1. search_feed_catalog(query="arxiv", category="science")
   → finds arXiv cs.AI, cs.LG, cs.CL feeds

2. subscribe_feed(url="https://rss.arxiv.org/rss/cs.AI")

3. collect_feeds(category="science")
   → fetches new entries

4. get_latest_articles(category="science", count=10)
   → returns latest papers
```

## Built-in Catalog

444 verified feeds across 6 categories. All audited — hard paywalls (Bloomberg, FT, WSJ) and broken URLs removed.

| Category | Feeds | Subcategories | Highlights |
|----------|------:|---------------|-----------|
| **technology** | 68 | ai_ml, developer, it_news, security, startup, ... | AWS, Cloudflare, Stripe, Netflix, HN, Go Blog, Rust Blog |
| **science** | 128 | journal, preprint, news, government | Nature, Science, arXiv, bioRxiv, medRxiv, NASA, PLOS |
| **society** | 119 | news_us, news_ko, news_uk, news_intl, factcheck, ... | BBC, NPR, NYT, NHK, JTBC, PolitiFact, Snopes |
| **finance** | 89 | markets, central_bank, regulatory, crypto | Fed, BOE, BOJ, SEC, CNBC, CoinDesk, Yahoo Finance |
| **pets** | 27 | veterinary, community, blog, health | AKC, PetMD, ASPCA, dvm360, r/dogs, r/cats |
| **academia** | 13 | ai_ml, research, institution | Google AI, DeepMind, Stanford HAI, Hugging Face |

**Languages:** English (381), Korean (47), Japanese (14), Chinese (2)

Full feed list: [CATALOG.md](CATALOG.md)

## Why FeedKit?

| | [awesome-rss-feeds](https://github.com/plenaryapp/awesome-rss-feeds) (2.1K★) | [engineering-blogs](https://github.com/kilimchoi/engineering-blogs) (37.5K★) | **FeedKit** |
|--|---|---|---|
| Type | Markdown list | Markdown list | **Python package** |
| Feeds | ~500 | ~600 | 444 |
| Scope | General | Tech blogs only | Tech + Science + Finance + News + Factcheck |
| Last update | 2021 (stale) | 2022 (stale) | **Active (daily collection)** |
| Verified working | No | No | **Yes (778K+ articles collected)** |
| Legal audit | No | No | **Yes (paywall/ToS feeds removed)** |
| CLI | No | No | **Yes (12 commands)** |
| Programmatic API | No | No | **Yes (async Python)** |
| MCP server | No | No | **Yes (9 tools)** |
| OPML | No | No | **Yes (import/export)** |
| FTS search | No | No | **Yes (SQLite FTS5)** |

## Disclaimer

This package distributes a catalog of **publicly available RSS feed URLs**, not the feed content itself. RSS is a syndication standard — publishing an RSS feed is an explicit invitation for readers to subscribe. FeedKit fetches feeds on the user's behalf and does not store or redistribute copyrighted content.

Feeds behind hard paywalls (Bloomberg, FT, WSJ, Barron's) and feeds with aggressive terms of service have been removed from the catalog.

## License

[MIT](LICENSE)

<!-- mcp-name: io.github.QuartzUnit/feedkit -->
