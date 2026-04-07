# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# Unauthorized copying, modification, or distribution of this file is prohibited.
import os
import logging

from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from app.core.config import settings

logger = logging.getLogger(__name__)


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

    def ingest_documents(self):
        supported_extensions = {".md", ".txt", ".html", ".htm", ".yaml", ".yml", ".py", ".js", ".json", ".css"}
        documents = []

        for root, _dirs, files in os.walk(self.knowledge_base_path):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in supported_extensions:
                    continue

                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    rel_path = os.path.relpath(filepath, self.knowledge_base_path)
                    chunks = self.text_splitter.split_text(content)

                    for i, chunk in enumerate(chunks):
                        documents.append({
                            "content": chunk,
                            "metadata": {
                                "source": rel_path,
                                "chunk_index": i,
                                "filename": filename,
                            },
                        })
                except Exception as e:
                    logger.error(f"Error reading {filepath}: {e}")

        if not documents:
            logger.warning("No documents found to ingest")
            return 0

        texts = [d["content"] for d in documents]
        metadatas = [d["metadata"] for d in documents]

        self.vectorstore = Chroma.from_texts(
            texts=texts,
            metadatas=metadatas,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.chroma_db_path,
        )

        logger.info(f"Ingested {len(documents)} chunks from {len(set(d['metadata']['source'] for d in documents))} files")
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
