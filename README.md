# SHL_test
A full-stack AI-powered SHL assessment recommender that scrapes product data and suggests relevant tests using LLMs. Built with FastAPI, LangChain, Groq, HuggingFace embeddings, and FAISS vector search.

# 🔍 SHL Assessment Recommender

A full-stack SHL test recommendation app using scraping + AI + vector search.

---

## ⚙️ Features

- Scrapes SHL assessment catalog using Selenium + aiohttp
- Stores extracted metadata in CSV
- Uses FAISS + HuggingFace embeddings for similarity search
- Calls Groq's LLM to generate human-readable suggestions
- FastAPI backend with optional static HTML frontend

---


---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/shl-recommender.git
cd shl-recommender

python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

### Run the scraper
python Scrapper.py

cd backend
uvicorn main:app --reload

Access static frontend (if needed):
http://127.0.0.1:8000/static/index.html

## Test API
python test.py

