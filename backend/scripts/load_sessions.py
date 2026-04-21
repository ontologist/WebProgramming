# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Populate the RAG vector store with sessions 1 through 6.

Sources:
  - Sessions 1-3: docs/lectures/sessionNN-<lang>.md and docs/slides/sessionNN-<lang>.md
                  (all 5 languages: en, ja, zh, ko, es)
  - Sessions 4-6: docs/weeks/week-0N/{lecture,slides,assignment,practice}.html
                  (HTML is stripped to plain text before indexing)

The existing Chroma collection is deleted first so this script is idempotent.

Usage:
    cd backend
    ./venv/Scripts/python.exe scripts/load_sessions.py
"""

from __future__ import annotations

import logging
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain.text_splitter import RecursiveCharacterTextSplitter  # noqa: E402
from langchain_community.embeddings import OllamaEmbeddings  # noqa: E402
from langchain_community.vectorstores import Chroma  # noqa: E402

from app.core.config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("load_sessions")


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs"
BACKEND = REPO_ROOT / "backend"

LANGUAGES = ["en", "ja", "zh", "ko", "es"]
MD_SESSIONS = [1, 2, 3]
HTML_SESSIONS = [4, 5, 6]
HTML_KINDS = ["lecture", "slides", "assignment", "practice"]


class _TextExtractor(HTMLParser):
    """Strip HTML tags, drop <style>/<script> bodies, keep readable text."""

    _SKIP = {"style", "script", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self._SKIP:
            self._skip_depth += 1
        elif tag in ("br", "p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section"):
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in ("p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section"):
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        # collapse runs of blank lines and trailing spaces
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in raw.splitlines()]
        cleaned: list[str] = []
        blank = False
        for ln in lines:
            if ln:
                cleaned.append(ln)
                blank = False
            elif not blank:
                cleaned.append("")
                blank = True
        return "\n".join(cleaned).strip()


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text()


def collect_documents() -> list[dict]:
    docs: list[dict] = []

    for n in MD_SESSIONS:
        for kind in ("lectures", "slides"):
            for lang in LANGUAGES:
                path = DOCS / kind / f"session{n:02d}-{lang}.md"
                if not path.exists():
                    logger.warning("missing %s", path.relative_to(REPO_ROOT))
                    continue
                docs.append({
                    "text": path.read_text(encoding="utf-8"),
                    "source": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "session": n,
                    "kind": kind.rstrip("s"),  # lecture / slide
                    "language": lang,
                })

    for n in HTML_SESSIONS:
        week_dir = DOCS / "weeks" / f"week-{n:02d}"
        for kind in HTML_KINDS:
            path = week_dir / f"{kind}.html"
            if not path.exists():
                continue
            text = html_to_text(path.read_text(encoding="utf-8"))
            if not text:
                logger.warning("empty after strip: %s", path.relative_to(REPO_ROOT))
                continue
            docs.append({
                "text": text,
                "source": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "session": n,
                "kind": kind,
                "language": "en",
            })

    return docs


def main() -> None:
    persist_dir = (BACKEND / "chroma_db").resolve()
    collection_name = f"course_knowledge_{settings.COURSE_ID}"

    print("=" * 60)
    print("WP-200 Sessions 1-6 Loader")
    print("=" * 60)
    print(f"persist dir     : {persist_dir}")
    print(f"collection      : {collection_name}")
    print(f"embedding model : {settings.OLLAMA_EMBEDDING_MODEL}")

    print("\nGathering source documents...")
    raw_docs = collect_documents()
    print(f"  found {len(raw_docs)} source files")
    for d in raw_docs:
        print(f"    - session {d['session']} {d['kind']:10s} [{d['language']}]  {d['source']}")

    if not raw_docs:
        print("nothing to ingest — aborting")
        sys.exit(1)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts: list[str] = []
    metadatas: list[dict] = []

    for d in raw_docs:
        for i, chunk in enumerate(splitter.split_text(d["text"])):
            texts.append(chunk)
            metadatas.append({
                "source": d["source"],
                "session": d["session"],
                "kind": d["kind"],
                "language": d["language"],
                "chunk_index": i,
            })

    print(f"\nSplit into {len(texts)} chunks")

    embeddings = OllamaEmbeddings(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_EMBEDDING_MODEL,
    )

    # Open the same collection the running backend uses. We empty it in place
    # (by deleting all current ids) rather than rmtree'ing the persist directory,
    # so the backend can stay up and its cached Chroma handle remains valid.
    store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
    )

    existing = store._collection.get()
    existing_ids = existing.get("ids", []) or []
    if existing_ids:
        print(f"Clearing {len(existing_ids)} existing chunks from collection...")
        store._collection.delete(ids=existing_ids)
    else:
        print("Collection is already empty.")

    print("Embedding and writing new chunks (this may take a minute)...")
    store.add_texts(texts=texts, metadatas=metadatas)

    count = store._collection.count()
    print(f"\nDone. Collection '{collection_name}' now holds {count} chunks.")
    print("Backend's RAGService shares this collection and will see the new content on its next query.")


if __name__ == "__main__":
    main()
