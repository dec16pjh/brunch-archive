# -*- coding: utf-8 -*-
import os, sys, json, time
import requests
sys.path.insert(0, os.path.dirname(__file__))
import brunch_lib

base = os.path.dirname(__file__)
meta = json.load(open(os.path.join(base, "books_meta.json"), encoding="utf-8"))

OUT_DIR = os.path.join(base, "full_data")
os.makedirs(OUT_DIR, exist_ok=True)

log_lines = []

def log(msg):
    log_lines.append(str(msg))

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def normalize_content(article):
    content = article.get("content_parsed") or {}
    cover = content.get("cover", {})
    title_sub = cover.get("title-sub", {})
    subtitle = brunch_lib.extract_text(title_sub.get("data")) if isinstance(title_sub, dict) else ""
    body_blocks = content.get("body", [])
    out_blocks = []
    for b in body_blocks:
        btype = b.get("type")
        if btype == "text":
            joined = brunch_lib.extract_text(b.get("data")).strip("\n")
            if joined.strip():
                out_blocks.append({"type": "p", "text": joined})
        elif btype == "quotation":
            joined = brunch_lib.extract_text(b.get("data")).strip("\n")
            if joined.strip():
                out_blocks.append({"type": "quote", "text": joined})
        elif btype == "img":
            out_blocks.append({
                "type": "img",
                "url": b.get("url"),
                "width": b.get("width"),
                "height": b.get("height"),
            })
        elif btype == "line":
            out_blocks.append({"type": "hr"})
    return subtitle, out_blocks


for slug, book in meta.items():
    out_path = os.path.join(OUT_DIR, f"{slug}.json")
    chapters = []
    chapter_no_counter = 0
    for part in book["parts"]:
        part_name = part["part"]
        for no in part["nos"]:
            chapter_no_counter += 1
            url = f"https://brunch.co.kr/@freeist/{no}"
            try:
                resp = session.get(url, timeout=20)
                raw = resp.text
            except Exception as e:
                log(f"FETCH ERROR {slug} no={no}: {e}")
                continue
            article = brunch_lib.parse_article_html(raw)
            if not article:
                log(f"NO ARTICLE DATA {slug} no={no}")
                continue
            subtitle, blocks = normalize_content(article)
            chapters.append({
                "seq": chapter_no_counter,
                "part": part_name,
                "no": no,
                "title": article.get("title", ""),
                "subtitle": subtitle,
                "date": article.get("publishTime"),
                "url": f"https://brunch.co.kr/@freeist/{no}",
                "blocks": blocks,
            })
            log(f"OK {slug} {chapter_no_counter:03d} no={no} title={article.get('title','')[:30]}")
    book_out = dict(book)
    book_out["slug"] = slug
    book_out["chapters"] = chapters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(book_out, f, ensure_ascii=False, indent=2)
    log(f"=== Saved {slug}: {len(chapters)} chapters ===")

with open(os.path.join(base, "fetch_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print("DONE. See fetch_log.txt")
