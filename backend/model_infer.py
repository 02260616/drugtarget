import requests
import json
import re

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = "4708c29a01364f9196a2351325898873.gBV5rspPUKI7JQeB"
MODEL_NAME = "glm-4.6"

SYSTEM_PROMPT = (
    "你是一个生物医学大模型，我将提供药物名称和 PubMed 文献句子。\n"
    "你需要分析药物可能的靶点、相关基因、相关通路及它们的置信度，必须使用 JSON 格式输出。"
)

def build_prompt(drug, sentences):
    sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)]) or "未检索到相关句子"

    return f"""
请分析药物 <{drug}> 的分子机制。

1. 你将基于句子推断：
   - Predicted_Targets
   - Related_Genes
   - Related_Pathways

2. JSON 输出格式示例：
{{
  "Drug": "{drug}",
  "Predicted_Targets": [
    {{"Target": "EGFR", "Confidence": "high", "Reasoning": "xxx"}}
  ],
  "Related_Genes": [
    {{"Gene": "EGFR", "Confidence": "high", "Reasoning": "yyy"}}
  ],
  "Related_Pathways": [
    {{"Pathway": "MAPK pathway", "Confidence": "medium", "Reasoning": "zzz"}}
  ]
}}

句子如下：
{sentences_text}
"""


def ask_llm(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    r = requests.post(API_URL, json=data, headers=headers)
    r.raise_for_status()

    text = r.json()["choices"][0]["message"]["content"].strip()
    return text


def parse_json(content):
    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except:
        # 尝试截取大括号
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1:
            try:
                return json.loads(cleaned[first:last+1])
            except:
                return None
        return None


def run_model_inference(drug, sentences):
    prompt = build_prompt(drug, sentences)
    raw = ask_llm(prompt)

   
    print("\n===== 模型返回原始内容 =====")
    print(raw)
    print("=================================\n")

    parsed = parse_json(raw)


    parsed = parse_json(raw)

    if not parsed:
        return {
            "Predicted_Targets": [],
            "Related_Genes": [],
            "Related_Pathways": []
        }

    def normalize(items, key):
        out = []
        if not isinstance(items, list):
            return []
        for it in items:
            if isinstance(it, dict):
                out.append({
                    key: it.get(key, ""),
                    "Confidence": it.get("Confidence", ""),
                })
        return out

    return {
        "Predicted_Targets": normalize(parsed.get("Predicted_Targets", []), "Target"),
        "Related_Genes": normalize(parsed.get("Related_Genes", []), "Gene"),
        "Related_Pathways": normalize(parsed.get("Related_Pathways", []), "Pathway"),
    }
