import asyncio
from fastapi import FastAPI
from app.routers import categorize, scenario, review, health
from app.db.pool import close_db_pool
from app.tasks.categorize_task import categorize_new_transactions
from app.routers import config
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.routers.config import show_config
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_id = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# index = faiss.read_index("vat_index.faiss")
# texts = load_text_chunks()  # Your original chunk list
# generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)



templates = Jinja2Templates(directory="app/templates")

app = FastAPI(title="FiscalGuide LLM API", version="1.0.0")

app.include_router(categorize.router, prefix="/transactions", tags=["Categorize"])
app.include_router(scenario.router, prefix="/transactions", tags=["Scenario"])
app.include_router(review.router, prefix="/transactions", tags=["Review"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(config.router, prefix="/system", tags=["System"])



@app.on_event("startup")
async def startup_event():
    global embedder, index, texts, generator

    def load_text_chunks():
        import json
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
    config = await show_config()
    return templates.TemplateResponse("dashboard.html", {"request": request, "config": config})

@app.post("/query")
async def query_model(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "") or data.get("userQuery", "")
    if not prompt:
        return {"error": "No prompt provided."}

    # Embed query
    query_embedding = embedder.encode([prompt], convert_to_numpy=True)
    D, I = index.search(np.array(query_embedding), k=5)
    retrieved_chunks = [texts[i] for i in I[0]]

    # Assemble prompt
    context = "\n".join(retrieved_chunks)
    final_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"

    # Generate response
    output = generator(final_prompt, max_new_tokens=300)
    return {"response": output[0]["generated_text"]}



