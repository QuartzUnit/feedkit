"""OPML import/export for feed subscriptions."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from feedkit.storage import FeedStore


def import_opml(store: FeedStore, path: str | Path) -> int:
    """Import feeds from an OPML file. Returns count of new subscriptions."""
    tree = ET.parse(path)
    root = tree.getroot()
    count = 0

    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl")
        if not xml_url:
            continue

        title = outline.get("title") or outline.get("text") or ""
        category = ""
        parent = _find_parent(root, outline)
        if parent is not None:
            category = parent.get("text") or parent.get("title") or ""

        store.subscribe(xml_url, title=title, category=category)
        count += 1

    return count


def export_opml(store: FeedStore, path: str | Path) -> int:
    """Export subscriptions to an OPML file. Returns count of feeds exported."""
    subs = store.list_subscriptions()

    root = ET.Element("opml", version="2.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = "FeedKit Subscriptions"

    body = ET.SubElement(root, "body")

    # Group by category
    categories: dict[str, list] = {}
    for s in subs:
        cat = s.category or "Uncategorized"
        categories.setdefault(cat, []).append(s)

    for cat, feeds in sorted(categories.items()):
        cat_outline = ET.SubElement(body, "outline", text=cat)
        for s in feeds:
            ET.SubElement(cat_outline, "outline",
                          type="rss",
                          text=s.title or s.feed_url,
                          title=s.title or "",
                          xmlUrl=s.feed_url)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return len(subs)


def _find_parent(root: ET.Element, child: ET.Element) -> ET.Element | None:
    """Find parent element of a child in XML tree."""
    for parent in root.iter():
        if child in list(parent):
            return parent
    return None
