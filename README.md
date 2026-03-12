# AI Backend Enterprise

Production-ready FastAPI backend for AI applications with RAG, LLM integration, and vector search.

## Features
- ✅ FastAPI with async support
- ✅ LLM integration (OpenAI, Anthropic, local)
- ✅ RAG pipeline with vector search
- ✅ Document ingestion (PDF, text)
- ✅ Celery background tasks
- ✅ PostgreSQL with pgvector
- ✅ Redis for caching and broker
- ✅ Docker compose setup

## Quick Start

```bash
cp .env.example .env
# Edit .env with your API keys
make install
make dev
