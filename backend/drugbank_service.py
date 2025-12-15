# drugbank_service.py
import xml.etree.ElementTree as ET

class DrugBankService:
    def __init__(self, xml_path: str):
        self.data = {}
        self._load(xml_path)

    def _load(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {"db": "http://www.drugbank.ca"}

        for drug in root.findall("db:drug", ns):
            names = set()

            name = drug.find("db:name", ns)
            if name is not None:
                names.add(name.text.lower())

            for syn in drug.findall("db:synonyms/db:synonym", ns):
                if syn.text:
                    names.add(syn.text.lower())

            for dbid in drug.findall("db:drugbank-id", ns):
                names.add(dbid.text.lower())

            targets = []
            for target in drug.findall("db:targets/db:target", ns):
                tname = target.find("db:name", ns)
                if tname is not None:
                    targets.append(tname.text.strip())

            for nm in names:
                self.data[nm] = targets

        print(f"[DrugBank] loaded {len(self.data)} drug keys")

    def query(self, drug_name: str):
        key = drug_name.lower().strip()
        if key in self.data:
            return {
                "in_drugbank": True,
                "targets": self.data[key]
            }
        return {
            "in_drugbank": False,
            "targets": []
        }
