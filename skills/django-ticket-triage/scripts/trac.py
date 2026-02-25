#!/usr/bin/env python3
"""Django Trac (code.djangoproject.com) access tools."""

from __future__ import annotations

import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

TRAC_BASE_URL = "https://code.djangoproject.com"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 5
BACKOFF_BASE = 1.0
BACKOFF_CAP = 30.0
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
HEADERS = {"User-Agent": "django-ticket-triage/0.2.0"}


def _strip_html(html: str) -> str:
    """Strip HTML tags and return plain text."""
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _parse_retry_after(value: str | None) -> float | None:
    """Return Retry-After delay in seconds when possible."""
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    if value.isdigit():
        return max(0.0, float(value))

    try:
        retry_dt = parsedate_to_datetime(value)
        if retry_dt.tzinfo is None:
            retry_dt = retry_dt.replace(tzinfo=timezone.utc)
        delta = (retry_dt - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, delta)
    except (TypeError, ValueError, OverflowError):
        return None


def _backoff_delay(attempt: int, retry_after: str | None = None) -> float:
    retry_after_seconds = _parse_retry_after(retry_after)
    if retry_after_seconds is not None:
        return retry_after_seconds

    exponential = min(BACKOFF_CAP, BACKOFF_BASE * (2 ** (attempt - 1)))
    jitter = random.uniform(0, exponential * 0.2)
    return exponential + jitter


def _request_bytes(url: str, params: dict[str, Any] | None = None) -> bytes:
    """Perform HTTP GET with retry/backoff for transient failures."""
    query = urlencode(params or {}, doseq=True)
    full_url = f"{url}?{query}" if query else url

    for attempt in range(1, MAX_RETRIES + 1):
        request = Request(full_url, headers=HEADERS, method="GET")
        try:
            with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                time.sleep(_backoff_delay(attempt, exc.headers.get("Retry-After")))
                continue
            raise
        except URLError:
            if attempt < MAX_RETRIES:
                time.sleep(_backoff_delay(attempt))
                continue
            raise


def _request_text(url: str, params: dict[str, Any] | None = None) -> str:
    return _request_bytes(url, params=params).decode("utf-8", errors="replace")


def get_ticket(ticket_id: int) -> dict[str, Any]:
    """
    Get ticket details by parsing HTML page.

    Returns:
        {
            "id": 36814,
            "summary": "During migration for rename m2m field...",
            "reporter": "dantyan",
            "owner": None,
            "component": "Migrations",
            "version": "6.0",
            "severity": "Normal",
            "status": "closed",
            "resolution": "duplicate",
            "keywords": ["migration", "manytomany"],
            "triage_stage": "Unreviewed",
            "has_patch": False,
            "created": "Dec 20, 2025, 8:56:37 AM",
            "last_modified": "Dec 23, 2025, 3:37:30 AM",
            "description": "...",
            "comments": [
                {"author": "Jacob Walls", "date": "...", "content": "..."}
            ]
        }
    """
    html = _request_text(f"{TRAC_BASE_URL}/ticket/{ticket_id}")

    # Extract old_values from JavaScript
    old_values = _extract_old_values(html)

    # Extract created and last_modified dates from date div
    created = None
    last_modified = None
    date_block = re.search(r'<div class="date">(.*?)</div>', html, re.DOTALL)
    if date_block:
        for m in re.finditer(
            r"<p[^>]*>(.*?)</p>", date_block.group(1), re.DOTALL
        ):
            p_html = m.group(1)
            # title format: "See timeline at Dec 20, 2025, 8:56:37 AM"
            link = re.search(
                r'<a[^>]*class="timeline"[^>]*title="See timeline at ([^"]+)"',
                p_html,
            )
            if link:
                date_str = link.group(1)
                p_text = _strip_html(p_html)
                if "Opened" in p_text:
                    created = date_str
                elif "Last modified" in p_text:
                    last_modified = date_str

    # Extract summary from title
    summary = ""
    title_m = re.search(r"<title>(.+?)</title>", html)
    if title_m:
        # Format: "#36814 (During migration...) – Django"
        match = re.search(r"#\d+\s*\((.+?)\)\s*[–-]", title_m.group(1))
        if match:
            summary = match.group(1)

    # Extract description
    description = ""
    desc_m = re.search(
        r'<div class="description">.*?<div class="searchable">(.*?)</div>',
        html,
        re.DOTALL,
    )
    if desc_m:
        description = _strip_html(desc_m.group(1))

    # Parse keywords
    keywords_str = old_values.get("keywords", "")
    keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

    # Get comments from RSS (more reliable parsing)
    comments = _get_comments_from_rss(ticket_id)

    return {
        "id": ticket_id,
        "summary": summary,
        "reporter": old_values.get("reporter") or None,
        "owner": old_values.get("owner") or None,
        "component": old_values.get("component") or None,
        "version": old_values.get("version") or None,
        "severity": old_values.get("severity") or None,
        "status": old_values.get("status") or None,
        "resolution": old_values.get("resolution") or None,
        "keywords": keywords,
        "triage_stage": old_values.get("stage") or None,
        "has_patch": old_values.get("has_patch") == "1",
        "created": created,
        "last_modified": last_modified,
        "description": description,
        "comments": comments,
    }


def _extract_old_values(html: str) -> dict[str, str]:
    """Extract old_values JavaScript object from HTML."""
    # Find old_values assignment and parse as JSON
    # The object can contain nested braces in string values, so we need careful parsing
    match = re.search(r"old_values\s*=\s*(\{)", html)
    if not match:
        return {}

    start = match.start(1)
    # Find matching closing brace by tracking brace depth
    depth = 0
    in_string = False
    escape_next = False
    end = start

    for i, char in enumerate(html[start:], start):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

    try:
        return json.loads(html[start:end])
    except json.JSONDecodeError:
        return {}


def _get_comments_from_rss(ticket_id: int) -> list[dict[str, str]]:
    """Get comments from RSS feed (easier to parse)."""
    content = _request_bytes(f"{TRAC_BASE_URL}/ticket/{ticket_id}?format=rss")

    comments = []
    root = ElementTree.fromstring(content)

    # RSS namespaces
    ns = {"dc": "http://purl.org/dc/elements/1.1/"}

    for item in root.findall(".//item"):
        author_elem = item.find("dc:creator", ns)
        date_elem = item.find("pubDate")
        desc_elem = item.find("description")

        author = author_elem.text if author_elem is not None else ""
        date = date_elem.text if date_elem is not None else ""
        content_text = ""
        if desc_elem is not None and desc_elem.text:
            # Parse HTML content
            content_text = _strip_html(desc_elem.text)

        comments.append({"author": author, "date": date, "content": content_text})

    return comments


def search(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    """
    Search Trac for tickets.

    Args:
        query: Search query (e.g., "ManyToManyField RenameField migration")
        max_results: Maximum number of results to return

    Returns:
        [{"id": 36800, "summary": "...", "status": "closed", "resolution": "..."}, ...]
    """
    html = _request_text(
        f"{TRAC_BASE_URL}/search",
        params={"q": query, "noquickjump": "1", "ticket": "on"},
    )

    results = []

    # Find search results - they're in <dl id="results">
    dl_match = re.search(r'<dl id="results">(.*?)</dl>', html, re.DOTALL)
    if not dl_match:
        return []

    # Each result is a <dt> with a link
    for dt_match in re.finditer(
        r"<dt>(.*?)</dt>", dl_match.group(1), re.DOTALL
    ):
        dt_html = dt_match.group(1)
        link = re.search(
            r'<a[^>]*href="[^"]*(/ticket/(\d+))"[^>]*>(.+?)</a>',
            dt_html,
            re.DOTALL,
        )
        if not link:
            continue

        ticket_id = int(link.group(2))
        # Parse link text: "#36800: Component: Summary (status: resolution)"
        link_text = _strip_html(link.group(3))

        # Extract summary and status
        summary = ""
        status = ""
        resolution = ""

        # Pattern: #ID: Component: Summary (status: resolution)
        text_match = re.match(
            r"#\d+:\s*(?:[^:]+:\s*)?(.+?)\s*(?:\((\w+)(?::\s*(\w+))?\))?$",
            link_text,
        )
        if text_match:
            summary = text_match.group(1).strip()
            status = text_match.group(2) or ""
            resolution = text_match.group(3) or ""

        results.append({
            "id": ticket_id,
            "summary": summary,
            "status": status,
            "resolution": resolution,
        })
        if len(results) >= max_results:
            break

    return results


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  trac.py get <ticket_id>")
        print("  trac.py search <query>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "get":
        if len(sys.argv) < 3:
            print("Error: ticket_id required")
            sys.exit(1)
        ticket_id = int(sys.argv[2])
        result = get_ticket(ticket_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: query required")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        results = search(query)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
