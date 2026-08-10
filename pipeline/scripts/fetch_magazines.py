# -*- coding: utf-8 -*-
import os, sys, json, time
import requests
sys.path.insert(0, os.path.dirname(__file__))
import brunch_lib

base = os.path.dirname(__file__)
OUT_DIR = os.path.join(base, "magazines_data")
os.makedirs(OUT_DIR, exist_ok=True)

MAGAZINES = {
    "sosohhanilsang": {"magazineNo": 170916, "title": "소소한 일상의 작은 느낌들", "genre": "에세이 · 일상"},
    "harutale": {"magazineNo": 286175, "title": "별에서 보내는 편지", "genre": "에세이 · 掌篇"},
    "greattoday": {"magazineNo": 271887, "title": "나의 하루", "genre": "에세이 · 일상"},
    "dailyquotes": {"magazineNo": 135629, "title": "매일 아침 힘을 주는 한 마디", "genre": "명언 · 잠언"},
}

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

log = []


def list_article_nos(magazine_no):
    nos = []
    create_time = 0
    while True:
        url = f"https://api.brunch.co.kr/v2/magazine/{magazine_no}/articles?createTime={create_time}&orderType=desc"
        resp = session.get(url, timeout=20)
        d = resp.json()
        data = d.get("data", {})
        items = data.get("list", [])
        for item in items:
            art = item.get("article", {})
            nos.append(art.get("no"))
        if not data.get("moreList"):
            break
        create_time = data.get("lastCreateTime")
        if not create_time:
            break
        time.sleep(0.1)
    return list(reversed(nos))  # chronological order


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
            out_blocks.append({"type": "img", "url": b.get("url"), "width": b.get("width"), "height": b.get("height")})
    return subtitle, out_blocks


for slug, minfo in MAGAZINES.items():
    log.append(f"=== {slug} (magazineNo={minfo['magazineNo']}) : listing ===")
    nos = list_article_nos(minfo["magazineNo"])
    log.append(f"  found {len(nos)} articles")
    chapters = []
    for i, no in enumerate(nos, 1):
        url = f"https://brunch.co.kr/@freeist/{no}"
        try:
            resp = session.get(url, timeout=20)
            raw = resp.text
        except Exception as e:
            log.append(f"FETCH ERROR {slug} no={no}: {e}")
            continue
        article = brunch_lib.parse_article_html(raw)
        if not article:
            log.append(f"NO ARTICLE DATA {slug} no={no}")
            continue
        subtitle, blocks = normalize_content(article)
        chapters.append({
            "seq": i,
            "no": no,
            "title": article.get("title", ""),
            "subtitle": subtitle,
            "date": article.get("publishTime"),
            "url": url,
            "blocks": blocks,
        })
        if i % 20 == 0:
            log.append(f"  ... {slug} {i}/{len(nos)}")
    out = dict(minfo)
    out["slug"] = slug
    out["chapters"] = chapters
    with open(os.path.join(OUT_DIR, f"{slug}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    log.append(f"=== Saved {slug}: {len(chapters)} chapters ===")

with open(os.path.join(base, "magazines_fetch_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print("DONE")
