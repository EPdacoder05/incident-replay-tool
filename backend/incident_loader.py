import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "incident.json"

def load_incidents():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}
