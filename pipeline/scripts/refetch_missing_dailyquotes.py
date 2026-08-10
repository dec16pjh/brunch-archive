# -*- coding: utf-8 -*-
import os, sys, json, time
import requests
sys.path.insert(0, os.path.dirname(__file__))
import brunch_lib
from fetch_magazines import list_article_nos, normalize_content, MAGAZINES

base = os.path.dirname(__file__)
OUT_DIR = os.path.join(base, "magazines_data")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

minfo = MAGAZINES["dailyquotes"]
all_nos = list_article_nos(minfo["magazineNo"])
print("total nos:", len(all_nos))

existing = json.load(open(os.path.join(OUT_DIR, "dailyquotes.json"), encoding="utf-8"))
existing_nos = {c["no"] for c in existing["chapters"]}
missing = [n for n in all_nos if n not in existing_nos]
print("missing:", len(missing), missing)

chapters_by_no = {c["no"]: c for c in existing["chapters"]}
log = []
for no in missing:
    ok = False
    for attempt in range(4):
        try:
            resp = session.get(f"https://brunch.co.kr/@freeist/{no}", timeout=20)
            raw = resp.text
            article = brunch_lib.parse_article_html(raw)
            if article:
                subtitle, blocks = normalize_content(article)
                chapters_by_no[no] = {
                    "seq": 0,  # will resequence below
                    "no": no,
                    "title": article.get("title", ""),
                    "subtitle": subtitle,
                    "date": article.get("publishTime"),
                    "url": f"https://brunch.co.kr/@freeist/{no}",
                    "blocks": blocks,
                }
                ok = True
                log.append(f"OK {no}")
                break
            else:
                log.append(f"RETRY {no} attempt{attempt}: no article")
        except Exception as e:
            log.append(f"RETRY {no} attempt{attempt}: {e}")
        time.sleep(2)
    if not ok:
        log.append(f"FAIL {no}")
    time.sleep(0.3)

# rebuild in correct order
new_chapters = []
for i, no in enumerate(all_nos, 1):
    if no in chapters_by_no:
        ch = chapters_by_no[no]
        ch["seq"] = i
        new_chapters.append(ch)

existing["chapters"] = new_chapters
with open(os.path.join(OUT_DIR, "dailyquotes.json"), "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

with open(os.path.join(base, "refetch_dailyquotes_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print("final count:", len(new_chapters))
