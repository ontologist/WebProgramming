<!-- Copyright (c) 2026 Yuri Tijerino. All rights reserved. -->
<!-- Unauthorized copying, modification, or distribution of this file is prohibited. -->

# WP-200 Backend - Setup Guide (Windows 11 + RTX 4090)

## Prerequisites

1. **Python 3.10+** - [python.org](https://www.python.org/downloads/)
2. **Ollama** - [ollama.com](https://ollama.com/download/windows)
3. **Docker Desktop** (optional, for PostgreSQL/Redis) - [docker.com](https://www.docker.com/products/docker-desktop/)
4. **CUDA** - Should already be installed for RTX 4090

## Quick Start

### 1. Install Ollama and models

```powershell
# After installing Ollama, pull the required models
ollama pull llama3.2:latest
ollama pull nomic-embed-text
```

### 2. Set up the backend

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy and edit configuration
copy .env.example .env
# Edit .env to set INSTRUCTOR_PASSWORD and JWT_SECRET
```

### 3. Load the knowledge base

```powershell
python scripts/load_knowledge_base.py
```

### 4. Start the server

```powershell
python app/main.py
```

The API will be available at `http://localhost:8001`
- API docs: `http://localhost:8001/docs`
- Instructor dashboard: `http://localhost:8001/dashboard`

### 5. (Optional) Start Docker services

Only needed if you want PostgreSQL/Redis instead of JSON file storage:

```powershell
docker-compose up -d
```

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/config.py        # Configuration (from .env)
│   ├── api/
│   │   ├── chat.py           # Bot chat endpoint
│   │   ├── submissions.py    # Student submission endpoint
│   │   └── instructor.py     # Instructor dashboard API
│   └── services/
│       ├── ollama_service.py  # Ollama LLM integration
│       ├── rag_service.py     # ChromaDB RAG pipeline
│       ├── bot_service.py     # Bot orchestration
│       ├── grading_service.py # Deterministic checks + AI grading
│       └── db_service.py      # JSON file database
├── dashboard/
│   └── index.html            # Instructor dashboard UI
├── knowledge_base/           # Course content for RAG
├── data/                     # Submissions database (auto-created)
├── chroma_db/                # Vector database (auto-created)
└── logs/                     # Application logs (auto-created)
```

## API Endpoints

### Student-facing
- `POST /api/chat` - Bot conversation
- `POST /api/submissions/submit` - Submit assignment
- `GET /api/submissions/grades/{student_id}` - View published grades

### Instructor (password-protected)
- `GET /api/instructor/submissions` - List all submissions
- `GET /api/instructor/submissions/{id}` - View submission detail
- `POST /api/instructor/submissions/{id}/review` - Review and grade
- `POST /api/instructor/submissions/{id}/publish` - Publish grade

## Exposing to Internet (for GitHub Pages)

The course site is hosted on GitHub Pages (HTTPS), so the backend needs HTTPS too.
Options:

### Cloudflare Tunnel (recommended)
```powershell
cloudflared tunnel --url http://localhost:8001
```

### ngrok
```powershell
ngrok http 8001
```

Then set the tunnel URL in the frontend:
```javascript
localStorage.setItem('bot_cloudflare_url', 'https://your-tunnel-url.com');
```
