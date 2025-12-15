# gdsc_service.py
import pandas as pd

class GDSCService:
    def __init__(self, csv_path: str):
        self.data = {}
        self._load(csv_path)

    def _load(self, csv_path):
        df = pd.read_csv(csv_path, encoding="utf-8", engine="python")

        col_drug = next(c for c in df.columns if "drug" in c.lower())
        col_target = next(c for c in df.columns if "target" in c.lower())
        col_pathway = next(c for c in df.columns if "pathway" in c.lower())
        col_gene = next((c for c in df.columns if "gene" in c.lower()), None)

        for _, row in df.iterrows():
            name = str(row[col_drug]).lower().strip()
            self.data[name] = {
                "target": str(row[col_target]),
                "pathway": str(row[col_pathway]),
                "gene": str(row[col_gene]) if col_gene else ""
            }

        print(f"[GDSC] loaded {len(self.data)} drugs")

    def query(self, drug_name: str):
        key = drug_name.lower().strip()
        if key in self.data:
            return {
                "in_GDSC": True,
                **self.data[key]
            }
        return {
            "in_GDSC": False,
            "target": "",
            "pathway": "",
            "gene": ""
        }
