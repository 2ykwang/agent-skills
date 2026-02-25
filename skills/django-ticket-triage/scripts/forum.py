#!/usr/bin/env python3
"""Django Forum (forum.djangoproject.com) access tools.

Django Forum is Discourse-based, so we use the Discourse API.
"""

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

FORUM_BASE_URL = "https://forum.djangoproject.com"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 5
BACKOFF_BASE = 1.0
BACKOFF_CAP = 30.0
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
HEADERS = {
    "User-Agent": "django-ticket-triage/0.2.0",
    "Accept": "application/json",
}

# Category IDs for reference
CATEGORIES = {
    "announcements": 7,
    "users": 6,  # "Using Django"
    "internals": 5,  # "Django Internals"
    "projects": 11,  # "Show & Tell"
    "events": 12,
    "packages": 30,
}


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


def _request_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = _request_bytes(url, params=params)
    return json.loads(payload.decode("utf-8", errors="replace"))


def search(
    query: str,
    category: str | None = None,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """
    Search Django Forum for topics.

    Args:
        query: Search query (e.g., "ManyToManyField default")
        category: Optional category slug (e.g., "internals", "users")
        max_results: Maximum number of results to return

    Returns:
        [
            {
                "id": 12345,
                "title": "Topic title",
                "slug": "topic-title",
                "url": "https://forum.djangoproject.com/t/topic-title/12345",
                "category_id": 5,
                "created_at": "2024-01-01T00:00:00.000Z",
                "posts_count": 5,
                "has_accepted_answer": True,
                "closed": False,
                "blurb": "Preview of the content..."
            },
            ...
        ]
    """
    params: dict[str, Any] = {"q": query}

    # Add category filter if specified
    if category and category in CATEGORIES:
        params["q"] = f"{query} ##{category}"

    data = _request_json(f"{FORUM_BASE_URL}/search.json", params=params)
    results = []

    # Extract topics from search results
    topics = data.get("topics", [])
    posts = data.get("posts", [])

    # Create a map of topic_id -> first matching post blurb
    topic_blurbs: dict[int, str] = {}
    for post in posts:
        topic_id = post.get("topic_id")
        if topic_id and topic_id not in topic_blurbs:
            topic_blurbs[topic_id] = post.get("blurb", "")

    for topic in topics[:max_results]:
        topic_id = topic.get("id")
        slug = topic.get("slug", "")

        results.append({
            "id": topic_id,
            "title": topic.get("title", ""),
            "slug": slug,
            "url": f"{FORUM_BASE_URL}/t/{slug}/{topic_id}",
            "category_id": topic.get("category_id"),
            "created_at": topic.get("created_at"),
            "posts_count": topic.get("posts_count", 0),
            "has_accepted_answer": topic.get("has_accepted_answer", False),
            "closed": topic.get("closed", False),
            "blurb": topic_blurbs.get(topic_id, ""),
        })

    return results


def get_topic(topic_id: int) -> dict[str, Any]:
    """
    Get topic details including posts.

    Args:
        topic_id: The topic ID

    Returns:
        {
            "id": 12345,
            "title": "Topic title",
            "slug": "topic-title",
            "url": "https://forum.djangoproject.com/t/topic-title/12345",
            "category_id": 5,
            "created_at": "2024-01-01T00:00:00.000Z",
            "posts_count": 5,
            "views": 100,
            "closed": False,
            "archived": False,
            "has_accepted_answer": True,
            "accepted_answer_post_number": 3,
            "posts": [
                {
                    "id": 111,
                    "post_number": 1,
                    "username": "user1",
                    "created_at": "...",
                    "content": "Post content...",
                    "like_count": 5,
                    "accepted_answer": False
                },
                ...
            ],
            "tags": ["tag1", "tag2"]
        }
    """
    data = _request_json(f"{FORUM_BASE_URL}/t/{topic_id}.json")

    canonical_id = data.get("id", topic_id)
    slug = data.get("slug", "")

    # Extract posts
    posts = []
    post_stream = data.get("post_stream", {})
    for post in post_stream.get("posts", []):
        # Clean HTML from cooked content
        content = post.get("cooked", "")
        # Simple HTML tag removal for preview
        content_text = re.sub(r"<[^>]+>", "", content).strip()

        posts.append({
            "id": post.get("id"),
            "post_number": post.get("post_number"),
            "username": post.get("username", ""),
            "name": post.get("name", ""),
            "created_at": post.get("created_at"),
            "content": content_text,
            "like_count": post.get("like_count", 0),
            "accepted_answer": post.get("accepted_answer", False),
        })

    return {
        "id": canonical_id,
        "title": data.get("title", ""),
        "slug": slug,
        "url": f"{FORUM_BASE_URL}/t/{slug}/{canonical_id}",
        "category_id": data.get("category_id"),
        "created_at": data.get("created_at"),
        "posts_count": data.get("posts_count", 0),
        "views": data.get("views", 0),
        "closed": data.get("closed", False),
        "archived": data.get("archived", False),
        "has_accepted_answer": data.get("has_accepted_answer", False),
        "accepted_answer_post_number": data.get("accepted_answer", {}).get(
            "post_number"
        ) if isinstance(data.get("accepted_answer"), dict) else None,
        "posts": posts,
        "tags": data.get("tags", []),
    }


def search_by_ticket(ticket_id: int) -> list[dict[str, Any]]:
    """
    Search forum for discussions mentioning a specific Trac ticket.

    Args:
        ticket_id: Django Trac ticket number

    Returns:
        List of topics mentioning the ticket
    """
    # Search for various ticket reference formats
    queries = [
        f"ticket {ticket_id}",
        f"#{ticket_id}",
        f"code.djangoproject.com/ticket/{ticket_id}",
    ]

    all_results: dict[int, dict[str, Any]] = {}

    for query in queries:
        results = search(query, max_results=10)
        for result in results:
            # Deduplicate by topic ID
            if result["id"] not in all_results:
                all_results[result["id"]] = result

    return list(all_results.values())


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  forum.py search <query> [--category=internals]")
        print("  forum.py get <topic_id>")
        print("  forum.py ticket <ticket_id>")
        print()
        print("Categories: announcements, users, internals, projects, events, packages")
        sys.exit(1)

    command = sys.argv[1]

    if command == "search":
        if len(sys.argv) < 3:
            print("Error: query required")
            sys.exit(1)

        # Parse arguments
        args = sys.argv[2:]
        category = None
        query_parts = []

        for arg in args:
            if arg.startswith("--category="):
                category = arg.split("=", 1)[1]
            else:
                query_parts.append(arg)

        query = " ".join(query_parts)
        results = search(query, category=category)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif command == "get":
        if len(sys.argv) < 3:
            print("Error: topic_id required")
            sys.exit(1)
        topic_id = int(sys.argv[2])
        result = get_topic(topic_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "ticket":
        if len(sys.argv) < 3:
            print("Error: ticket_id required")
            sys.exit(1)
        ticket_id = int(sys.argv[2])
        results = search_by_ticket(ticket_id)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
