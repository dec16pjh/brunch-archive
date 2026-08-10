# -*- coding: utf-8 -*-
import sys, os, json, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "brunch_pilot"))
from book_data import BOOK, CHAPTERS

chapters = []
for ch in CHAPTERS:
    blocks = []
    for para in ch["body"].split("\n\n"):
        para = para.strip()
        if not para:
            continue
        is_quote = para.startswith(">>>")
        if is_quote:
            para = para[3:].strip()
        blocks.append({"type": "quote" if is_quote else "p", "text": para})
    dt = datetime.datetime.strptime(ch["date"], "%Y-%m-%d")
    chapters.append({
        "seq": ch["no"],
        "part": ch["part"],
        "no": None,
        "title": ch["title"],
        "subtitle": ch["subtitle"],
        "date": int(dt.timestamp() * 1000),
        "url": ch["url"],
        "blocks": blocks,
    })

out = {
    "title": BOOK["title"],
    "genre": BOOK["genre"],
    "release_date": BOOK["release_date"],
    "slug": "grit2success",
    "chapters": chapters,
}

out_path = os.path.join(os.path.dirname(__file__), "full_data", "grit2success.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("chapters:", len(chapters))
