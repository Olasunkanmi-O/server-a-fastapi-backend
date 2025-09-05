# app/main.py

# app/main.py

import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.routers import categorize, scenario, review, health, config
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.routers import categorize, scenario, review, health, config
from app.db.pool import close_db_pool
from app.tasks.categorize_task import categorize_new_transactions
from app.routers.config import show_config
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import faiss
import numpy as np
import json
import httpx
from app.config import settings
import json
import httpx
from app.config import settings



templates = Jinja2Templates(directory="app/templates")
app = FastAPI(title="FiscalGuide LLM API", version="1.0.0")

# Routers
# Routers
app.include_router(categorize.router, prefix="/transactions", tags=["Categorize"])
app.include_router(scenario.router, prefix="/transactions", tags=["Scenario"])
app.include_router(review.router, prefix="/transactions", tags=["Review"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(config.router, prefix="/system", tags=["System"])

# Globals
embedder = None
index = None
texts = None
generator = None
# Globals
embedder = None
index = None
texts = None
generator = None

@app.on_event("startup")
async def startup_event():
    global embedder, index, texts, generator

    def load_text_chunks():
        with open("chunks_with_meta.json", "r") as f:
            data = json.load(f)
            return [item["text"] for item in data]
        
        

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("vat_index.faiss")
    texts = load_text_chunks()

    model_id = "microsoft/phi-2"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)

    asyncio.create_task(periodic_categorization())
    asyncio.create_task(test_llm_call())

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()

async def periodic_categorization():
    while True:
        await categorize_new_transactions()
        await asyncio.sleep(60)

@app.get("/")
async def root():
    return {"message": "FiscalGuide LLM API is running!"}

@app.get("/admin")
async def admin_dashboard(request: Request):
    config_data = await show_config()
    return templates.TemplateResponse("dashboard.html", {"request": request, "config": config_data})
    config_data = await show_config()
    return templates.TemplateResponse("dashboard.html", {"request": request, "config": config_data})

@app.post("/query")
async def query_model(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "") or data.get("userQuery", "")
    if not prompt:
        return {"error": "No prompt provided."}

    query_embedding = embedder.encode([prompt], convert_to_numpy=True)
    D, I = index.search(np.array(query_embedding), k=5)
    retrieved_chunks = [texts[i] for i in I[0]]

    context = "\n".join(retrieved_chunks)
    final_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"

    output = generator(final_prompt, max_new_tokens=300)
    return {"response": output[0]["generated_text"]}

async def call_llm(prompt: str, provider: str = settings.DEFAULT_PROVIDER):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://13.220.51.63:8000/providers/{provider}",
                json={"prompt": prompt}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"LLM call failed: {str(e)}"}
async def test_llm_call():
    response = await call_llm("Categorize this transaction: Uber ride on Friday", provider="google")
    print(response)
