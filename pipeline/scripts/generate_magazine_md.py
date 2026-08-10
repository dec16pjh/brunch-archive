# -*- coding: utf-8 -*-
import os, json, shutil, datetime

base = os.path.dirname(__file__)
DATA_DIR = os.path.join(base, "magazines_data")
IMG_DIR = os.path.join(base, "images")
SITE = os.path.join(base, "brunch_pilot", "site")
MAGS_DIR = os.path.join(SITE, "_magazines")
ASSETS_IMG = os.path.join(SITE, "assets", "images")
os.makedirs(MAGS_DIR, exist_ok=True)
os.makedirs(ASSETS_IMG, exist_ok=True)


def fm_escape(s):
    return (s or "").replace('"', '\\"')


def html_escape(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_date(ts):
    if not ts:
        return "1970-01-01"
    try:
        return datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
    except Exception:
        return "1970-01-01"


def img_filename(slug, seq, url):
    import hashlib
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        ext = ".jpg"
    return f"{slug}_{seq:03d}_{h}{ext}"


def block_to_md(block, slug, seq_hint):
    if block["type"] == "img":
        url = block.get("url")
        if not url:
            return ""
        fname = img_filename(slug, seq_hint, url)
        local_path = os.path.join(IMG_DIR, fname)
        if not os.path.exists(local_path):
            try:
                import requests
                from PIL import Image
                from io import BytesIO
                sess = requests.Session()
                sess.headers.update({"User-Agent": "Mozilla/5.0"})
                resp = sess.get(url, timeout=25)
                im = Image.open(BytesIO(resp.content))
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                w, h = im.size
                if w > 1400:
                    ratio = 1400 / w
                    im = im.resize((1400, int(h * ratio)))
                im.save(local_path, quality=85, optimize=True)
            except Exception:
                return ""
        if not os.path.exists(os.path.join(ASSETS_IMG, fname)):
            shutil.copy(local_path, os.path.join(ASSETS_IMG, fname))
        return f"![]({{{{ '/assets/images/{fname}' | relative_url }}}})"
    text = html_escape(block.get("text", ""))
    if not text.strip():
        return ""
    if block["type"] == "quote":
        lines = text.split("\n")
        return "\n".join(f"> {l}" for l in lines)
    return text.replace("\n", "  \n")


def build_magazine(mag):
    slug = mag["slug"]
    mag_dir = os.path.join(MAGS_DIR, slug)
    os.makedirs(mag_dir, exist_ok=True)

    chapters = mag["chapters"]
    for i, ch in enumerate(chapters):
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i < len(chapters) - 1 else None
        fname = f"{ch['seq']:03d}.md"
        path = os.path.join(mag_dir, fname)

        img_seq = 0
        body_parts = []
        for b in ch["blocks"]:
            if b["type"] == "img":
                img_seq += 1
            body_parts.append(block_to_md(b, slug, ch["seq"] * 10 + img_seq))
        body_md = "\n\n".join(p for p in body_parts if p)

        fm = [
            "---",
            "layout: chapter",
            f'title: "{fm_escape(ch["title"])}"',
            f'subtitle: "{fm_escape(ch["subtitle"])}"',
            f'book: "{fm_escape(mag["title"])}"',
            f'book_slug: "magazines/{slug}"',
            'part: ""',
            f'genre: "{fm_escape(mag["genre"])}"',
            f'chapter_no: {ch["seq"]}',
            f'date: {fmt_date(ch["date"])}',
            f'source_url: "{ch["url"]}"',
            f'index_url: "/magazine-archive/{slug}/"',
            f'prev_title: "{fm_escape(prev_ch["title"]) if prev_ch else ""}"',
            f'prev_url: "{("/magazines/%s/%03d/" % (slug, prev_ch["seq"])) if prev_ch else ""}"',
            f'next_title: "{fm_escape(next_ch["title"]) if next_ch else ""}"',
            f'next_url: "{("/magazines/%s/%03d/" % (slug, next_ch["seq"])) if next_ch else ""}"',
            "---",
            "",
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(fm) + body_md + "\n")

    idx_path = os.path.join(MAGS_DIR, f"{slug}-index.md")
    lines = [
        "---",
        "layout: book_index",
        f'title: "{fm_escape(mag["title"])}"',
        f'book_slug: "magazines/{slug}"',
        f'genre: "{fm_escape(mag["genre"])}"',
        f'author: "박종호"',
        f'release_date: ""',
        f'permalink: /magazine-archive/{slug}/',
        "---",
        "",
        f"매거진 원문: [brunch.co.kr/magazine/{slug}](https://brunch.co.kr/magazine/{slug})",
        "",
        "## 글 목록",
        "",
    ]
    for ch in chapters:
        lines.append(f'- [{ch["seq"]:03d}. {html_escape(ch["title"])}]({{{{ "/magazines/{slug}/{ch["seq"]:03d}/" | relative_url }}}})')
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return len(chapters)


if __name__ == "__main__":
    total = 0
    for fn in sorted(os.listdir(DATA_DIR)):
        mag = json.load(open(os.path.join(DATA_DIR, fn), encoding="utf-8"))
        n = build_magazine(mag)
        total += n
        print(mag["slug"], n)
    print("TOTAL", total)
