# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Shared utilities for per-assignment graders. Pure stdlib — no soup.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

_WS = re.compile(r"\s+")

_BLOCK_TAGS = {"p", "div", "section", "article", "li", "br",
               "h1", "h2", "h3", "h4", "h5", "h6",
               "header", "footer", "nav", "main", "aside"}
_SKIP_TAGS = {"style", "script", "noscript", "template"}


class _TextExtractor(HTMLParser):
    """Collect visible text. Inserts newlines at block boundaries so
    paragraph-level comparison is meaningful."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip += 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS and self._skip > 0:
            self._skip -= 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip == 0:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def html_to_paragraphs(html: str) -> list[str]:
    """Return non-empty, whitespace-normalized text blocks from HTML."""
    if not html:
        return []
    ext = _TextExtractor()
    try:
        ext.feed(html)
    except Exception:
        return []
    raw = ext.text()
    out: list[str] = []
    for line in raw.splitlines():
        norm = _WS.sub(" ", line).strip()
        if norm:
            out.append(norm)
    return out


def extract_hrefs(html: str) -> list[str]:
    """Collect the values of every `<a href="...">` in the document."""
    hrefs: list[str] = []

    class _P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                for k, v in attrs:
                    if k == "href" and v:
                        hrefs.append(v.strip())

    p = _P()
    try:
        p.feed(html or "")
    except Exception:
        pass
    return hrefs


def extract_inline_css(html: str) -> str:
    """Return the concatenated body of every <style>...</style> block."""
    chunks: list[str] = []

    class _P(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self._in_style = False

        def handle_starttag(self, tag, attrs):
            if tag == "style":
                self._in_style = True

        def handle_endtag(self, tag):
            if tag == "style":
                self._in_style = False

        def handle_data(self, data):
            if self._in_style:
                chunks.append(data)

    p = _P()
    try:
        p.feed(html or "")
    except Exception:
        pass
    return "\n".join(chunks)


def count_tag_mismatches(html: str) -> int:
    """Rough well-formedness count: unclosed opens + orphan closes.
    Void elements are not expected to close."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}
    stack: list[str] = []
    orphans = 0

    class _P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag in VOID:
                return
            stack.append(tag)

        def handle_endtag(self, tag):
            nonlocal orphans
            if tag in VOID:
                return
            # Walk up to find matching open
            for i in range(len(stack) - 1, -1, -1):
                if stack[i] == tag:
                    # Anything above this open is an unclosed tag
                    orphans += len(stack) - 1 - i
                    del stack[i:]
                    return
            orphans += 1  # closing tag with no matching open

        def handle_startendtag(self, tag, attrs):
            return  # self-closing; ignore

    p = _P()
    try:
        p.feed(html or "")
    except Exception:
        return 10
    return orphans + len(stack)


def load_template(template_dir: Path) -> dict[str, str]:
    """Read every .htm/.html in template_dir into a name->content dict."""
    out: dict[str, str] = {}
    if not template_dir.exists():
        return out
    for p in template_dir.iterdir():
        if p.is_file() and p.suffix.lower() in {".htm", ".html"}:
            try:
                out[p.name.lower()] = p.read_text(encoding="utf-8")
            except Exception:
                pass
    return out


def all_html_text(files: dict | None) -> str:
    """Concatenate the content of every uploaded HTM/HTML file."""
    if not files:
        return ""
    buf: list[str] = []
    for name, content in files.items():
        if not isinstance(content, str):
            continue
        lname = name.lower()
        if lname.endswith((".htm", ".html", ".css")):
            buf.append(content)
    return "\n".join(buf)
