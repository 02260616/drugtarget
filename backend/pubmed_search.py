import re
import time
from Bio import Entrez
from pylitsense.pylitsense import PyLitSense

Entrez.email = "your_email@example.com"
pls = PyLitSense()

# ================= 关键词 =================
MOA_KEYWORDS = [
    "mechanism of action", "moa", "mechanism",
    "target", "inhibits", "activates", "binds",
    "receptor", "enzyme", "protein"
]

PHARMACO_KEYWORDS = [
    "pharmacokinetics", "pharmacodynamics", "metabolism"
]

ALL_KEYWORDS = MOA_KEYWORDS + PHARMACO_KEYWORDS


# ================= PubMed =================
def search_pubmed_ids(drug, retmax=8):
    """等价于 search_pubmed_abstracts"""
    keyword_query = " OR ".join([f'"{kw}"' for kw in ALL_KEYWORDS])
    query = f'"{drug}" AND ({keyword_query})'

    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=retmax,
        sort="relevance"
    )
    record = Entrez.read(handle)
    handle.close()

    return record.get("IdList", [])


def fetch_pubmed_abstracts(ids):
    """拉取多个 PMID 的摘要"""
    abstracts = {}
    for pmid in ids:
        handle = Entrez.efetch(
            db="pubmed",
            id=pmid,
            rettype="abstract",
            retmode="text"
        )
        abstracts[pmid] = handle.read()
        handle.close()
        time.sleep(0.3)
    return abstracts


def extract_sentences(text):
    """只负责切句，不做过滤"""
    if not text:
        return []
    return re.split(r'(?<=[.!?])\s+', text)


def _filter_strict(sentences, drug):
    """严格：药物名 + 关键词"""
    hits = []
    drug_low = drug.lower()
    for s in sentences:
        s_low = s.lower()
        if drug_low in s_low and any(k.lower() in s_low for k in ALL_KEYWORDS):
            hits.append(s.strip())
    return hits


def _filter_loose(sentences, drug):
    """宽松：只要药物名"""
    hits = []
    drug_low = drug.lower()
    for s in sentences:
        if drug_low in s.lower():
            hits.append(s.strip())
    return hits


def get_pubmed_sentences(drug):
    """
    行为与新代码一致：
    - 先严格
    - 不足 10 条 → 用宽松补
    - 返回句子列表（不破坏原有返回结构）
    """
    pmids = search_pubmed_ids(drug)
    abstracts = fetch_pubmed_abstracts(pmids)

    strict_hits = []
    loose_hits = []

    for pmid, abstract in abstracts.items():
        sentences = extract_sentences(abstract)

        for s in _filter_strict(sentences, drug):
            strict_hits.append(s)

        for s in _filter_loose(sentences, drug):
            loose_hits.append(s)

    if len(strict_hits) >= 10:
        return strict_hits[:10]

    # 严格 + 宽松去重
    combined = strict_hits.copy()
    seen = set(strict_hits)

    for s in loose_hits:
        if s not in seen:
            combined.append(s)
            seen.add(s)

    return combined[:10]


# ================= LitSense =================
def litsense_hits(drug):
    """
    等价于 search_litsense_sentences
    - 严格：药物 + 关键词
    - 不足 10 → 用宽松补
    """
    query = f"{drug} " + " OR ".join(ALL_KEYWORDS)
    results = pls.query(query)

    strict_hits = []
    loose_hits = []

    for r in results[:50]:
        text_low = r.text.lower()
        has_drug = drug.lower() in text_low
        has_kw = any(k.lower() in text_low for k in ALL_KEYWORDS)

        if has_drug and has_kw:
            strict_hits.append(r.text)

        if has_drug:
            loose_hits.append(r.text)

    if len(strict_hits) >= 10:
        return strict_hits[:10]

    combined = strict_hits.copy()
    seen = set(strict_hits)

    for s in loose_hits:
        if s not in seen:
            combined.append(s)
            seen.add(s)

    return combined[:10]
