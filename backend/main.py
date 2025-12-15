from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model_infer import run_model_inference
from pubmed_search import get_pubmed_sentences

from drugbank_service import DrugBankService
from gdsc_service import GDSCService

# ================= FastAPI =================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= 启动时加载大文件 =================
drugbank = DrugBankService("data/full database.xml")
gdsc = GDSCService("data/GDSC_all.csv")

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

    # ---------- DrugBank / GDSC ----------
    drugbank_info = drugbank.query(drug)
    gdsc_info = gdsc.query(drug)

    # ---------- Return (as requested) ----------
    return {
        "drug": drug,
        "literature_sentences": sentences,

        "targets": attach_evidence(
            model_result["Predicted_Targets"],
            "Target",
            drugbank_info,
            gdsc_info
        ),

        "genes": attach_evidence(
            model_result["Related_Genes"],
            "Gene",
            drugbank_info,
            gdsc_info
        ),

        "pathways": attach_evidence(
            model_result["Related_Pathways"],
            "Pathway",
            drugbank_info,
            gdsc_info
        )
    }



def attach_evidence(items, key, drugbank_info, gdsc_info):
    """
    items: model inference list
    key: "Target" / "Gene" / "Pathway"
    """
    out = []

    for it in items:
        name = it.get(key, "")

        # ---------- DrugBank ----------
        in_drugbank = (
            drugbank_info.get("in_drugbank", False)
            and name in drugbank_info.get("targets", [])
        )

        # ---------- GDSC ----------
        in_gdsc = False
        if gdsc_info.get("in_GDSC", False):
            if key == "Gene":
                in_gdsc = name == gdsc_info.get("gene")
            elif key == "Pathway":
                in_gdsc = name == gdsc_info.get("pathway")
            elif key == "Target":
                in_gdsc = name == gdsc_info.get("target")

        out.append({
            key: name,
            "Confidence": it.get("Confidence", ""),
            "DrugBank": in_drugbank,
            "GDSC": in_gdsc
        })

    return out
