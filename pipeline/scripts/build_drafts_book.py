import json, os, datetime

base = os.path.dirname(__file__)
raw = json.load(open(os.path.join(base, "drafts_export.json"), encoding="utf-8"))

items = []
for r in raw:
    if "data" not in r:
        continue
    d = r["data"]
    items.append({
        "no": r["no"],
        "title": (d.get("title") or "").strip(),
        "subtitle": (d.get("subtitle") or "").strip(),
        "date": d.get("date"),
        "blocks": d.get("blocks", []),
        "url": f"https://brunch.co.kr/@freeist/{r['no']}",
    })

items.sort(key=lambda x: x["date"] or 0)

for i, it in enumerate(items, 1):
    it["seq"] = i
    it["part"] = ""

img_count = sum(1 for it in items for b in it["blocks"] if b["type"] == "img")

book = {
    "title": "서랍 (미발행 초고 모음)",
    "genre": "서랍 · 미발행 초고",
    "author": "박종호",
    "release_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    "slug": "drawer",
    "chapters": items,
}

out_path = os.path.join(base, "full_data", "drawer.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(book, f, ensure_ascii=False, indent=2)

print("chapters:", len(items), "images:", img_count)
for it in items:
    dt = datetime.datetime.fromtimestamp(it["date"]/1000).strftime("%Y-%m-%d") if it["date"] else "?"
    print(it["seq"], dt, it["title"])
