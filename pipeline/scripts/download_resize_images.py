# -*- coding: utf-8 -*-
import os, json, hashlib
import requests
from PIL import Image
from io import BytesIO

base = os.path.dirname(__file__)
DATA_DIR = os.path.join(base, "full_data")
IMG_DIR = os.path.join(base, "images")
os.makedirs(IMG_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

MAX_W_PRINT = 1000   # px, for docx/pdf embedding
MAX_W_WEB = 1400      # px, for web/blog

log = []

def img_filename(slug, seq, url):
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        ext = ".jpg"
    return f"{slug}_{seq:03d}_{h}{ext}"

for fn in sorted(os.listdir(DATA_DIR)):
    path = os.path.join(DATA_DIR, fn)
    book = json.load(open(path, encoding="utf-8"))
    slug = book["slug"]
    changed = False
    for ch in book["chapters"]:
        img_seq = 0
        for block in ch["blocks"]:
            if block["type"] != "img":
                continue
            img_seq += 1
            url = block["url"]
            if not url:
                continue
            fname = img_filename(slug, ch["seq"] * 10 + img_seq, url)
            local_path = os.path.join(IMG_DIR, fname)
            web_fname = fname.replace(os.path.splitext(fname)[1], ".jpg") if False else fname
            if not os.path.exists(local_path):
                try:
                    resp = session.get(url, timeout=25)
                    im = Image.open(BytesIO(resp.content))
                    if im.mode in ("RGBA", "P"):
                        im = im.convert("RGB")
                    w, h = im.size
                    if w > MAX_W_WEB:
                        ratio = MAX_W_WEB / w
                        im = im.resize((MAX_W_WEB, int(h * ratio)))
                    im.save(local_path, quality=85, optimize=True)
                    log.append(f"OK {slug} seq{ch['seq']} img{img_seq} {url} -> {fname}")
                except Exception as e:
                    log.append(f"FAIL {slug} seq{ch['seq']} img{img_seq} {url} : {e}")
                    continue
            block["local_file"] = fname
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(book, f, ensure_ascii=False, indent=2)

with open(os.path.join(base, "image_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print("DONE", len(log))
