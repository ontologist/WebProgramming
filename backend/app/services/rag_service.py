# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
import os
import re
import logging
from html.parser import HTMLParser

from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from app.core.config import settings

logger = logging.getLogger(__name__)


class _VisibleTextExtractor(HTMLParser):
    """Extract visible text from HTML, skipping style/script/head content."""
    _SKIP_TAGS = {"style", "script", "head", "noscript"}

    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data)

    def text(self):
        joined = " ".join(self._chunks)
        return re.sub(r"\s+", " ", joined).strip()


def _html_to_text(content: str) -> str:
    parser = _VisibleTextExtractor()
    try:
        parser.feed(content)
    except Exception as e:
        logger.warning(f"HTML parse failed, falling back to raw content: {e}")
        return content
    return parser.text()


def _resolve_docs_weeks_root() -> str | None:
    """Locate docs/weeks/ relative to backend/ — mirrors the resolution in main.py."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "weeks"),
        os.path.join(os.getcwd(), "..", "docs", "weeks"),
        os.path.join(os.getcwd(), "docs", "weeks"),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.isdir(p):
            return os.path.abspath(p)
    return None


class RAGService:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_EMBEDDING_MODEL,
        )
        self.chroma_db_path = settings.CHROMA_DB_PATH
        self.knowledge_base_path = settings.KNOWLEDGE_BASE_PATH
        self.collection_name = f"course_knowledge_{settings.COURSE_ID}"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.vectorstore = None
        self._init_vectorstore()

    def _init_vectorstore(self):
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.chroma_db_path,
            )
            count = self.vectorstore._collection.count()
            logger.info(f"RAG initialized with {count} documents in collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to initialize vectorstore: {e}")

    def _clear_collection(self):
        """Empty the live collection in place (preserves Chroma persist dir / avoids lock issues)."""
        if not self.vectorstore:
            return 0
        try:
            existing = self.vectorstore._collection.get(include=[])
            ids = existing.get("ids", []) if isinstance(existing, dict) else []
            if ids:
                self.vectorstore._collection.delete(ids=ids)
            return len(ids)
        except Exception as e:
            logger.warning(f"Could not clear collection (may be empty): {e}")
            return 0

    def _read_text(self, filepath: str, ext: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if ext in {".html", ".htm"}:
            return _html_to_text(content)
        return content

    def ingest_documents(self):
        supported_extensions = {".md", ".txt", ".html", ".htm", ".yaml", ".yml", ".py", ".js", ".json", ".css"}
        documents = []

        # 1. Knowledge base (markdown + auxiliary files)
        if os.path.isdir(self.knowledge_base_path):
            for root, _dirs, files in os.walk(self.knowledge_base_path):
                for filename in files:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in supported_extensions:
                        continue
                    filepath = os.path.join(root, filename)
                    try:
                        text = self._read_text(filepath, ext)
                        if not text.strip():
                            continue
                        rel_path = os.path.relpath(filepath, self.knowledge_base_path)
                        for i, chunk in enumerate(self.text_splitter.split_text(text)):
                            documents.append({
                                "content": chunk,
                                "metadata": {
                                    "source": f"knowledge_base/{rel_path}",
                                    "chunk_index": i,
                                    "filename": filename,
                                    "doc_type": "knowledge_base",
                                },
                            })
                    except Exception as e:
                        logger.error(f"Error reading {filepath}: {e}")

        # 2. Course site weeks (lecture / slides / assignment HTML)
        weeks_root = _resolve_docs_weeks_root()
        if weeks_root:
            week_dirs = sorted(
                d for d in os.listdir(weeks_root)
                if d.startswith("week-") and os.path.isdir(os.path.join(weeks_root, d))
            )
            for week_dir in week_dirs:
                week_label = week_dir  # e.g. "week-10"
                for filename in ("lecture.html", "slides.html", "assignment.html"):
                    filepath = os.path.join(weeks_root, week_dir, filename)
                    if not os.path.isfile(filepath):
                        continue
                    try:
                        text = self._read_text(filepath, ".html")
                        if not text.strip():
                            continue
                        doc_type = filename.split(".")[0]  # lecture | slides | assignment
                        for i, chunk in enumerate(self.text_splitter.split_text(text)):
                            documents.append({
                                "content": chunk,
                                "metadata": {
                                    "source": f"weeks/{week_label}/{filename}",
                                    "chunk_index": i,
                                    "filename": filename,
                                    "week": week_label,
                                    "doc_type": doc_type,
                                },
                            })
                    except Exception as e:
                        logger.error(f"Error reading {filepath}: {e}")
        else:
            logger.warning("docs/weeks/ not found; weekly lecture/slides/assignment content will not be in RAG")

        if not documents:
            logger.warning("No documents found to ingest")
            return 0

        cleared = self._clear_collection()
        if cleared:
            logger.info(f"Cleared {cleared} existing chunks before re-ingest")

        texts = [d["content"] for d in documents]
        metadatas = [d["metadata"] for d in documents]

        self.vectorstore = Chroma.from_texts(
            texts=texts,
            metadatas=metadatas,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.chroma_db_path,
        )

        unique_sources = len(set(d["metadata"]["source"] for d in documents))
        logger.info(f"Ingested {len(documents)} chunks from {unique_sources} files")
        return len(documents)

    def retrieve_context(self, query: str, k: int = 5) -> list:
        if not self.vectorstore:
            return []

        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def build_context(self, query: str, k: int = 5) -> str:
        results = self.retrieve_context(query, k)
        if not results:
            return ""

        context_parts = []
        for r in results:
            context_parts.append(f"[Source: {r['source']}]\n{r['content']}")

        return "\n\n---\n\n".join(context_parts)

    def get_collection_info(self) -> dict:
        if not self.vectorstore:
            return {"status": "not initialized", "count": 0}

        try:
            count = self.vectorstore._collection.count()
            return {"status": "ready", "count": count}
        except Exception:
            return {"status": "error", "count": 0}


rag_service = RAGService()
