# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Script to load course documents into ChromaDB for RAG.

Usage:
    cd backend
    python scripts/load_knowledge_base.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.rag_service import rag_service


def main():
    print("=" * 60)
    print("WP-200 Knowledge Base Loader")
    print("=" * 60)

    # Check knowledge base directory
    kb_path = rag_service.knowledge_base_path
    if not os.path.exists(kb_path):
        print(f"ERROR: Knowledge base directory not found: {kb_path}")
        sys.exit(1)

    # Count files
    file_count = 0
    for root, dirs, files in os.walk(kb_path):
        for f in files:
            file_count += 1
    print(f"Found {file_count} files in {kb_path}")

    # Ingest documents
    print("\nIngesting documents into ChromaDB...")
    chunk_count = rag_service.ingest_documents()
    print(f"Ingested {chunk_count} chunks")

    # Show collection info
    info = rag_service.get_collection_info()
    print(f"\nCollection info: {info}")

    print("\nDone! Knowledge base is ready for RAG queries.")


if __name__ == "__main__":
    main()
