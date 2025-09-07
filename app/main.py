# app/main.py

import asyncio
import json
import faiss
import numpy as np
import httpx
import requests
import time

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.db.pool import close_db_pool
from app.tasks.categorize_task import categorize_new_transactions
from app.routers.config import show_config

# Routers
from app.routers import categorize, scenario, review, health, config
from app.routers.scenario import router as scenario_router

# Templates
templates = Jinja2Templates(directory="app/admin_monitoring/templates")

# App Initialization
app = FastAPI(title="FiscalGuide LLM API", version="1.0.0")

# Global Embedding Resources
embedder = None
index = None
texts = None

# -------------------- ROUTER REGISTRATION --------------------

app.include_router(categorize.router, prefix="/transactions", tags=["Categorization"])
app.include_router(scenario.router, prefix="/transactions", tags=["Scenario Simulation"])
app.include_router(review.router, prefix="/transactions", tags=["Review Logs"])
app.include_router(health.router, prefix="/health", tags=["Health Checks"])
app.include_router(config.router, prefix="/system", tags=["System Config"])

# -------------------- STARTUP & SHUTDOWN --------------------

@app.on_event("startup")
async def startup_event():
    global embedder, index, texts

    def load_text_chunks():
        with open("chunks_with_meta.json", "r") as f:
            data = json.load(f)
            return [item["text"] for item in data]

    print(f" LLM endpoint configured as: {settings.LLM_ENDPOINT}")
    server_d_alive = await ping_server_d()
    print(f" Server D reachable: {server_d_alive}")

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("vat_index.faiss")
    texts = load_text_chunks()

    asyncio.create_task(periodic_categorization())
    #asyncio.create_task(test_llm_call())

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()

# -------------------- BACKGROUND TASKS --------------------

async def periodic_categorization():
    while True:
        await categorize_new_transactions()
        await asyncio.sleep(60)

async def test_llm_call():
    response = await call_llm("Categorize this transaction: Uber ride on Friday")
    print(f" LLM test response: {response}")

# -------------------- ROUTES --------------------

@app.get("/")
async def root():
    return {"message": "FiscalGuide LLM API is running!"}

@app.get("/admin")
async def admin_dashboard(request: Request):
    config_data = await show_config()
    return templates.TemplateResponse("dashboard.html", {"request": request, "config": config_data})

@app.post("/query")
async def query_model(request: Request):
    import time  # Needed for sleep
    data = await request.json()
    prompt = data.get("prompt", "") or data.get("userQuery", "")
    raw_id = data.get("user_id", 123)
    if not str(raw_id).isdigit():
        return {"error": "user_id must be numeric."}
    user_id = int(raw_id)


    if not prompt:
        return {"error": "No prompt provided."}

    route = "/scenario" if prompt.lower().startswith("what if") else "/llm/infer"
    print(f"Routing prompt to: {route}")
    

    try:
        if route == "/scenario":
            scenario_payload = {
                "user_id": user_id,
                "request": prompt
            }
            print(f"Sending to /scenario: {scenario_payload}")

            for attempt in range(3):
                try:
                    scenario_response = requests.post(
                        f"http://44.220.141.173:8000{route}",
                        json=scenario_payload,
                        timeout=200
                    )
                    if scenario_response.status_code == 200:
                        return scenario_response.json()
                    else:
                        print(f"Attempt {attempt + 1} failed with status {scenario_response.status_code}")
                        break
                except requests.exceptions.ReadTimeout:
                    print(f"Attempt {attempt + 1} timed out. Retrying...")
                    time.sleep(2)

            # Fallback to direct LLM inference
            fallback_response = requests.post(
                "http://44.220.141.173:8000/llm/infer",
                json={"prompt": prompt},
                timeout=20
            )
            return fallback_response.json()

        # Direct LLM inference for non-scenario prompts
        llm_response = requests.post(
            f"http://44.220.141.173:8000{route}",
            json={"prompt": prompt},
            timeout=20
        )
        return llm_response.json()

    except Exception as e:
        return {
            "response": "Unable to process request.",
            "error": str(e)
        }
   

# -------------------- LLM ORCHESTRATION --------------------

async def call_llm(prompt: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(settings.LLM_ENDPOINT, json={"prompt": prompt})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f" LLM call failed: {str(e)}")
            return {
                "response": "Unable to generate scenario.",
                "confidence": None,
                "source_model": "mistral-7b",
                "error": str(e)
            }

async def ping_server_d() -> bool:
    async with httpx.AsyncClient() as client:
        try:
            ping_url = settings.LLM_ENDPOINT.replace("/infer", "/ping")
            res = await client.get(ping_url)
            return res.status_code == 200
        except Exception as e:
            print(f" Server D ping failed: {str(e)}")
            return False