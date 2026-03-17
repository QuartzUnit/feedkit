"""SQLite storage — subscriptions, articles, FTS5 search."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path.home() / ".feedkit" / "feedkit.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS subscriptions (
    feed_url    TEXT PRIMARY KEY,
    title       TEXT DEFAULT '',
    category    TEXT DEFAULT '',
    language    TEXT DEFAULT 'en',
    added_at    TEXT DEFAULT (datetime('now')),
    last_fetch  TEXT,
    fetch_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_error  TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    guid        TEXT PRIMARY KEY,
    feed_url    TEXT REFERENCES subscriptions(feed_url) ON DELETE CASCADE,
    title       TEXT DEFAULT '',
    url         TEXT DEFAULT '',
    summary     TEXT DEFAULT '',
    author      TEXT DEFAULT '',
    published   TEXT,
    fetched_at  TEXT DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    title, summary, author,
    content='articles',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, summary, author)
    VALUES (new.rowid, new.title, new.summary, new.author);
END;

CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, summary, author)
    VALUES ('delete', old.rowid, old.title, old.summary, old.author);
END;
"""


@dataclass
class Subscription:
    feed_url: str
    title: str = ""
    category: str = ""
    language: str = "en"
    added_at: str = ""
    last_fetch: str | None = None
    fetch_count: int = 0
    error_count: int = 0
    last_error: str | None = None


@dataclass
class Article:
    guid: str
    feed_url: str
    title: str = ""
    url: str = ""
    summary: str = ""
    author: str = ""
    published: str | None = None
    fetched_at: str = ""


class FeedStore:
    """SQLite-backed feed subscription and article store."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)

    def close(self) -> None:
        self._conn.close()

    # === Subscriptions ===

    def subscribe(self, feed_url: str, title: str = "", category: str = "", language: str = "en") -> None:
        """Add a feed subscription."""
        self._conn.execute(
            "INSERT OR IGNORE INTO subscriptions (feed_url, title, category, language) VALUES (?, ?, ?, ?)",
            (feed_url, title, category, language),
        )
        self._conn.commit()

    def unsubscribe(self, feed_url: str) -> None:
        """Remove a feed subscription and its articles."""
        self._conn.execute("DELETE FROM subscriptions WHERE feed_url = ?", (feed_url,))
        self._conn.commit()

    def list_subscriptions(self) -> list[Subscription]:
        """List all subscriptions."""
        rows = self._conn.execute("SELECT * FROM subscriptions ORDER BY category, title").fetchall()
        return [Subscription(**dict(r)) for r in rows]

    def subscription_count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]

    # === Articles ===

    def save_articles(self, articles: list[Article]) -> int:
        """Save articles, skipping duplicates. Returns count of new articles."""
        new = 0
        for a in articles:
            try:
                self._conn.execute(
                    "INSERT INTO articles (guid, feed_url, title, url, summary, author, published) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (a.guid, a.feed_url, a.title, a.url, a.summary, a.author, a.published),
                )
                new += 1
            except sqlite3.IntegrityError:
                pass
        self._conn.commit()
        return new

    def article_count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]

    def get_latest(self, count: int = 20, category: str = "") -> list[Article]:
        """Get latest articles, optionally filtered by subscription category."""
        if category:
            rows = self._conn.execute(
                "SELECT a.* FROM articles a JOIN subscriptions s ON a.feed_url = s.feed_url "
                "WHERE s.category = ? ORDER BY a.fetched_at DESC LIMIT ?",
                (category, count),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM articles ORDER BY fetched_at DESC LIMIT ?", (count,)
            ).fetchall()
        return [Article(**dict(r)) for r in rows]

    def search(self, query: str, count: int = 20) -> list[Article]:
        """Full-text search across articles."""
        rows = self._conn.execute(
            "SELECT a.* FROM articles a JOIN articles_fts f ON a.rowid = f.rowid "
            "WHERE articles_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, count),
        ).fetchall()
        return [Article(**dict(r)) for r in rows]

    # === Feed Health ===

    def update_fetch_status(self, feed_url: str, success: bool, error: str = "") -> None:
        """Update fetch status for a subscription."""
        now = datetime.now(timezone.utc).isoformat()
        if success:
            self._conn.execute(
                "UPDATE subscriptions SET last_fetch = ?, fetch_count = fetch_count + 1, last_error = NULL WHERE feed_url = ?",
                (now, feed_url),
            )
        else:
            self._conn.execute(
                "UPDATE subscriptions SET error_count = error_count + 1, last_error = ? WHERE feed_url = ?",
                (error, feed_url),
            )
        self._conn.commit()

    def get_health(self) -> list[dict]:
        """Get feed health status."""
        rows = self._conn.execute(
            "SELECT feed_url, title, fetch_count, error_count, last_fetch, last_error "
            "FROM subscriptions ORDER BY error_count DESC"
        ).fetchall()
        return [dict(r) for r in rows]
