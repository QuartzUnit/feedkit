"""CLI entry point — python -m feedkit or `feedkit` command."""

import asyncio
import json
import sys

import click
from rich.console import Console
from rich.table import Table

from feedkit import __version__
from feedkit.catalog import get_catalog_stats, list_categories, search_catalog
from feedkit.core import collect, fetch_feed
from feedkit.storage import FeedStore

console = Console()


def _get_store():
    return FeedStore()


@click.group()
@click.version_option(__version__, prog_name="feedkit")
def main():
    """FeedKit — RSS/Atom feed collection with curated catalog."""


@main.command()
@click.argument("query", default="")
@click.option("--category", "-c", default="", help="Filter by category")
@click.option("--language", "-l", default="", help="Filter by language (en, ko, ...)")
@click.option("--limit", "-n", default=20, help="Max results")
@click.option("--json-output", "-j", is_flag=True, help="JSON output")
def search(query, category, language, limit, json_output):
    """Search the built-in feed catalog."""
    results = search_catalog(query, category=category, language=language, limit=limit)

    if json_output:
        data = [{"url": f.url, "title": f.title, "category": f.category, "language": f.language} for f in results]
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        table = Table(title=f"Catalog Search: {query or '(all)'} ({len(results)} results)")
        table.add_column("Title", style="cyan", max_width=40)
        table.add_column("Category", style="green")
        table.add_column("Lang")
        table.add_column("URL", style="dim", max_width=50)
        for f in results:
            table.add_row(f.title, f.category, f.language, f.url)
        console.print(table)


@main.command()
@click.argument("url")
@click.option("--category", "-c", default="", help="Category for this subscription")
@click.option("--title", "-t", default="", help="Title override")
def subscribe(url, category, title):
    """Subscribe to a feed."""
    store = _get_store()
    store.subscribe(url, title=title, category=category)
    console.print(f"[green]✓[/green] Subscribed to {url}")
    store.close()


@main.command()
@click.argument("url")
def unsubscribe(url):
    """Unsubscribe from a feed."""
    store = _get_store()
    store.unsubscribe(url)
    console.print(f"[yellow]✓[/yellow] Unsubscribed from {url}")
    store.close()


@main.command("list")
def list_subs():
    """List all subscriptions."""
    store = _get_store()
    subs = store.list_subscriptions()

    if not subs:
        console.print("[dim]No subscriptions yet. Use `feedkit subscribe <url>` or `feedkit subscribe-catalog`.[/dim]")
    else:
        table = Table(title=f"Subscriptions ({len(subs)})")
        table.add_column("Title", style="cyan", max_width=35)
        table.add_column("Category", style="green")
        table.add_column("Fetched", justify="right")
        table.add_column("Errors", justify="right")
        for s in subs:
            table.add_row(s.title or s.feed_url[:35], s.category, str(s.fetch_count), str(s.error_count))
        console.print(table)

    store.close()


@main.command("subscribe-catalog")
@click.option("--category", "-c", required=True, help="Subscribe to all feeds in this category")
def subscribe_catalog(category):
    """Subscribe to all feeds in a catalog category."""
    feeds = search_catalog(category=category, limit=1000)
    if not feeds:
        console.print(f"[red]No feeds found in category '{category}'[/red]")
        return

    store = _get_store()
    for f in feeds:
        store.subscribe(f.url, title=f.title, category=f.category, language=f.language)
    console.print(f"[green]✓[/green] Subscribed to {len(feeds)} feeds in category '{category}'")
    store.close()


@main.command("collect")
@click.option("--category", "-c", default="", help="Only collect from this category")
@click.option("--concurrency", "-n", default=20, help="Max concurrent requests")
def collect_cmd(category, concurrency):
    """Collect articles from all subscribed feeds."""
    store = _get_store()
    sub_count = store.subscription_count()

    if sub_count == 0:
        console.print("[dim]No subscriptions. Use `feedkit subscribe` first.[/dim]")
        store.close()
        return

    console.print(f"Collecting from {sub_count} feeds...")

    try:
        result = asyncio.run(collect(store, category=category, concurrency=concurrency))
    except KeyboardInterrupt:
        sys.exit(130)

    console.print(f"[green]✓[/green] {result.feeds_ok}/{result.feeds_total} feeds OK, "
                  f"{result.new_articles} new articles, {result.duration_ms:.0f}ms")
    if result.errors:
        console.print(f"[yellow]{result.feeds_error} feeds failed[/yellow]")

    store.close()


@main.command()
@click.argument("query")
@click.option("--count", "-n", default=20, help="Max results")
def find(query, count):
    """Full-text search across collected articles."""
    store = _get_store()
    articles = store.search(query, count=count)

    if not articles:
        console.print("[dim]No matching articles found.[/dim]")
    else:
        table = Table(title=f"Search: '{query}' ({len(articles)} results)")
        table.add_column("Title", style="cyan", max_width=50)
        table.add_column("Published")
        table.add_column("URL", style="dim", max_width=50)
        for a in articles:
            table.add_row(a.title[:50], a.published or "", a.url[:50])
        console.print(table)

    store.close()


@main.command()
@click.option("--count", "-n", default=20, help="Number of articles")
@click.option("--category", "-c", default="", help="Filter by category")
def latest(count, category):
    """Show latest collected articles."""
    store = _get_store()
    articles = store.get_latest(count=count, category=category)

    if not articles:
        console.print("[dim]No articles yet. Run `feedkit collect` first.[/dim]")
    else:
        table = Table(title=f"Latest Articles ({len(articles)})")
        table.add_column("Title", style="cyan", max_width=50)
        table.add_column("Published")
        table.add_column("Feed", style="dim", max_width=30)
        for a in articles:
            table.add_row(a.title[:50], a.published or "", a.feed_url[:30])
        console.print(table)

    store.close()


@main.command()
def stats():
    """Show catalog and subscription statistics."""
    cat_stats = get_catalog_stats()
    console.print(f"\n[bold]Catalog:[/bold] {cat_stats['total_feeds']} feeds")
    for cat, n in cat_stats["categories"].items():
        console.print(f"  {cat}: {n}")

    store = _get_store()
    sub_count = store.subscription_count()
    art_count = store.article_count()
    console.print(f"\n[bold]Local:[/bold] {sub_count} subscriptions, {art_count} articles")
    store.close()


@main.command("categories")
def categories_cmd():
    """List available catalog categories."""
    for cat in list_categories():
        console.print(f"  {cat}")


@main.command("import-opml")
@click.argument("path")
def import_opml_cmd(path):
    """Import feeds from an OPML file."""
    from feedkit.opml import import_opml

    store = _get_store()
    count = import_opml(store, path)
    console.print(f"[green]✓[/green] Imported {count} feeds from {path}")
    store.close()


@main.command("export-opml")
@click.argument("path")
def export_opml_cmd(path):
    """Export subscriptions to an OPML file."""
    from feedkit.opml import export_opml

    store = _get_store()
    count = export_opml(store, path)
    console.print(f"[green]✓[/green] Exported {count} feeds to {path}")
    store.close()


if __name__ == "__main__":
    main()
