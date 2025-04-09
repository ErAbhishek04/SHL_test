import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain_community.vectorstores import FAISS
from langchain.schema.document import Document
from langchain_huggingface import HuggingFaceEmbeddings

from openai import OpenAI  # ✅ New SDK

from newspaper import Article

def fetch_text_from_url(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return f"Error fetching text from URL: {e}"


# === Configuration ===
# CSV_PATH ="shl_product_catalog.csv"
INDEX_PATH = "faiss_csv_index"
GROQ_API_KEY = "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"  # Replace with your Groq API key
GROQ_MODEL = "llama3-70b-8192"  # ✅ Updated supported model

# === Init FastAPI ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

# === Load LangChain Embedding Wrapper ===
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# === Load CSV into Documents ===
def load_documents_from_csv():
    df = pd.read_csv("https://raw.githubusercontent.com/ErAbhishek04/SHL_test/main/backend/shl_product_catalog.csv")

    documents = []
    for i, row in df.iterrows():
        metadata = row.to_dict()
        content = f"{row['Description']}. Job Levels: {row['Job Levels']}. Language: {row['Language']}"
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

# === Load or Create Vector Store ===
if os.path.exists(INDEX_PATH):
    vector_store = FAISS.load_local(INDEX_PATH, embedding, allow_dangerous_deserialization=True)
else:
    docs = load_documents_from_csv()
    vector_store = FAISS.from_documents(docs, embedding)
    vector_store.save_local(INDEX_PATH)

# === Setup Groq Client ===
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# === Endpoint ===
@app.post("/recommend")
async def recommend_tests(q: Query):
    query = q.query
    results = vector_store.similarity_search(query, k=10)

    # Prepare prompt data
    prompt_info = []
    for doc in results:
        meta = doc.metadata
        prompt_info.append(
            f"- {meta.get('Product Name')} ({meta.get('Link')}): Remote: {meta.get('Remote Testing')}, "
            f"Adaptive: {meta.get('Adaptive/IRT')}, Duration: {meta.get('Duration')}, "
            f"Type: {meta.get('Test Type')}"
        )

    # Generate summary via Groq
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an intelligent assistant that recommends SHL assessments based on job descriptions."
            },
            {
                "role": "user",
                "content": (
                    f"Given the job description:\n\"\"\"\n{query}\n\"\"\"\n\n"
                    f"Here are some potentially relevant SHL assessments:\n{chr(10).join(prompt_info)}\n\n"
                    "Now write a short paragraph recommendation for each assessment that is most suitable."
                )
            }
        ]
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages
        )
        groq_text = response.choices[0].message.content.strip()
    except Exception as e:
        groq_text = f"Groq response not available: {str(e)}"

    # Filter only tests mentioned in Groq's response
    selected_tests = []
    for doc in results:
        meta = doc.metadata
        product_name = meta.get("Product Name", "")
        if product_name.lower() in groq_text.lower():
            selected_tests.append({
                "url": meta.get("Link"),
                "adaptive_support": "Yes" if meta.get("Adaptive/IRT", "").lower() == "yes" else "No",
                "description": meta.get("Description"),
                "duration": int(meta.get("Duration", 0)),
                "remote_support": "Yes" if meta.get("Remote Testing", "").lower() == "yes" else "No",
                "test_type": [meta.get("Test Type")] if isinstance(meta.get("Test Type"), str) else []
            })

    return {
        "recommended_assessments": selected_tests,
        "llm_summary": groq_text
    }
