from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model_infer import run_model_inference
from pubmed_search import get_pubmed_sentences

# ================= FastAPI =================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= 请求模型 =================
class DrugRequest(BaseModel):
    drug_name: str


@app.post("/query_drug")
def query_drug(req: DrugRequest):
    drug = req.drug_name.strip()

    # ---------- PubMed ----------
    sentences = get_pubmed_sentences(drug)

    # ---------- LLM ----------
    model_result = run_model_inference(drug, sentences)

    # ---------- Return ----------
    return {
        "drug": drug,
        "literature_sentences": sentences,
        "targets": model_result.get("Predicted_Targets", []),
        "genes": model_result.get("Related_Genes", []),
        "pathways": model_result.get("Related_Pathways", [])
    }
