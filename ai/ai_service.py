import os, time, threading
from typing import List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

MODEL_REPO = os.getenv("MODEL_REPO", "bartowski/Qwen2.5-3B-Instruct-GGUF")
MODEL_FILE = os.getenv("MODEL_FILE", "Qwen2.5-3B-Instruct-Q4_K_M.gguf")
N_CTX = int(os.getenv("N_CTX", "4096"))
N_THREADS = int(os.getenv("N_THREADS", "4"))
N_BATCH = int(os.getenv("N_BATCH", "128"))

app = FastAPI(title="JoeAI Local Marketing AI", version="2.0.0")

llm = None
model_path = None
lock = threading.Lock()

SYSTEM = """
You are JoeAI, a senior restaurant revenue operator and CRM strategist.

You are not a generic assistant.
You specialize in:
- churn and retention
- customer segmentation
- WhatsApp CRM campaigns
- menu profitability
- AOV and LTV improvement
- repeat customer growth
- restaurant accounting insights
- local business growth in Italy

Rules:
- Answer the exact user question first.
- Use the provided restaurant data.
- Use prior chat history when available.
- Be specific, numerical and operational.
- If the user asks a definition, define it clearly before giving strategy.
- For campaigns, write practical WhatsApp messages in Italian.
- Never invent fake data outside the context.
"""

class ChatMessage(BaseModel):
    role: str
    content: str

class MarketingRequest(BaseModel):
    restaurant: Dict[str, Any]
    kpis: Dict[str, Any]
    top_items: List[Dict[str, Any]] = []
    top_customers: List[Dict[str, Any]] = []
    history: List[ChatMessage] = []
    task: str

def load_model():
    global llm, model_path
    if llm is not None:
        return llm

    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        local_dir="/models",
    )

    llm = Llama(
        model_path=model_path,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_batch=N_BATCH,
        verbose=False,
    )
    return llm

@app.on_event("startup")
def startup():
    load_model()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "joeai_ai",
        "version": "2.0.0",
        "model_repo": MODEL_REPO,
        "model_file": MODEL_FILE,
        "model_path": model_path,
        "n_ctx": N_CTX,
        "n_threads": N_THREADS,
    }

@app.post("/marketing")
def marketing(req: MarketingRequest):
    model = load_model()

    compact_kpis = {
        "customers": req.kpis.get("customers"),
        "orders": req.kpis.get("orders"),
        "revenue": req.kpis.get("total_revenue"),
        "aov": req.kpis.get("avg_order"),
        "margin": req.kpis.get("gross_margin_estimate"),
        "churn_risk_rate": req.kpis.get("churn_risk_rate"),
        "inactive_customers": req.kpis.get("inactive"),
        "cold_customers": req.kpis.get("cold"),
        "repeat_rate": req.kpis.get("repeat_rate"),
        "ltv_estimate": req.kpis.get("ltv_estimate"),
        "estimated_app_value": req.kpis.get("estimated_app_value"),
    }

    history_text = ""
    for m in req.history[-8:]:
        role = "User" if m.role == "user" else "JoeAI"
        history_text += f"{role}: {m.content[:500]}\n"

    prompt = f"""<|im_start|>system
{SYSTEM}
<|im_end|>
<|im_start|>user
Restaurant:
{req.restaurant}

Restaurant metrics:
{compact_kpis}

Top selling items:
{req.top_items[:8]}

Top customers:
{req.top_customers[:8]}

Chat history:
{history_text}

Current user question:
{req.task}

Answer format:
- Direct answer
- What the data says
- Recommended action
- If relevant, WhatsApp message in Italian

Use enough detail to be useful, but do not ramble.
<|im_end|>
<|im_start|>assistant
"""

    started = time.time()

    try:
        with lock:
            out = model(
                prompt[:7000],
                max_tokens=420,
                temperature=0.35,
                top_p=0.88,
                stop=["<|im_end|>", "<|endoftext|>"],
            )

        return {
            "answer": out["choices"][0]["text"].strip(),
            "seconds": round(time.time() - started, 2),
            "model": MODEL_FILE,
            "n_ctx": N_CTX,
        }

    except BaseException as e:
        return {
            "answer": f"AI generation failed: {type(e).__name__}: {str(e)}",
            "seconds": round(time.time() - started, 2),
            "model": MODEL_FILE,
            "n_ctx": N_CTX,
        }
