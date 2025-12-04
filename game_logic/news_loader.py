import json
from pathlib import Path

NEWS_PATH = Path(__file__).resolve().parent.parent / "data" / "news" / "news.json"


def load_news():
    with open(NEWS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
