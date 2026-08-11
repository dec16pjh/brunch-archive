# -*- coding: utf-8 -*-
import os, json, shutil, datetime, re

base = os.path.dirname(__file__)
DATA_DIR = os.path.join(base, "full_data")
IMG_DIR = os.path.join(base, "images")
SITE = os.path.join(base, "brunch_pilot", "site")
BOOKS_DIR = os.path.join(SITE, "_brunchbooks")
ASSETS_IMG = os.path.join(SITE, "assets", "images")
os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(ASSETS_IMG, exist_ok=True)


def fm_escape(s):
    return (s or "").replace('"', '\\"')


def html_escape(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_md_leading(line):
    # kramdown reads a line-start "1. ", "- ", "* ", "+ ", "# " as a list/heading marker.
    # Escape so the original character shows literally instead of being parsed as markdown.
    m = re.match(r"^(\s*)(\d+)\.(\s)", line)
    if m:
        return f"{m.group(1)}{m.group(2)}\\.{m.group(3)}{line[m.end():]}"
    m = re.match(r"^(\s*)([-*+#])(\s)", line)
    if m:
        return f"{m.group(1)}\\{m.group(2)}{m.group(3)}{line[m.end():]}"
    return line


def escape_md_block(text):
    return "\n".join(escape_md_leading(l) for l in text.split("\n"))


def fmt_date(ts):
    if not ts:
        return ""
    try:
        return datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
    except Exception:
        return ""


def block_to_md(block):
    if block["type"] == "img":
        fname = block.get("local_file")
        if not fname:
            return ""
        if not os.path.exists(os.path.join(ASSETS_IMG, fname)):
            src = os.path.join(IMG_DIR, fname)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(ASSETS_IMG, fname))
        return f"![]({{{{ '/assets/images/{fname}' | relative_url }}}})"
    text = html_escape(block.get("text", ""))
    if not text.strip():
        return ""
    text = escape_md_block(text)
    if block["type"] == "quote":
        lines = text.split("\n")
        return "\n".join(f"> {l}" for l in lines)
    return text.replace("\n", "  \n")


def build_book(book):
    slug = book["slug"]
    book_dir = os.path.join(BOOKS_DIR, slug)
    os.makedirs(book_dir, exist_ok=True)

    chapters = book["chapters"]
    for i, ch in enumerate(chapters):
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i < len(chapters) - 1 else None
        fname = f"{ch['seq']:02d}.md"
        path = os.path.join(book_dir, fname)

        body_parts = [block_to_md(b) for b in ch["blocks"]]
        body_md = "\n\n".join(p for p in body_parts if p)

        fm = [
            "---",
            "layout: chapter",
            f'title: "{fm_escape(ch["title"])}"',
            f'subtitle: "{fm_escape(ch["subtitle"])}"',
            f'book: "{fm_escape(book["title"])}"',
            f'book_slug: "{slug}"',
            f'part: "{fm_escape(ch["part"])}"',
            f'genre: "{fm_escape(book["genre"])}"',
            f'chapter_no: {ch["seq"]}',
            f'date: {fmt_date(ch["date"]) or "1970-01-01"}',
            f'source_url: "{ch["url"]}"',
            f'index_url: "/brunchbook/{slug}/"',
            f'prev_title: "{fm_escape(prev_ch["title"]) if prev_ch else ""}"',
            f'prev_url: "{("/brunchbooks/%s/%02d/" % (slug, prev_ch["seq"])) if prev_ch else ""}"',
            f'next_title: "{fm_escape(next_ch["title"]) if next_ch else ""}"',
            f'next_url: "{("/brunchbooks/%s/%02d/" % (slug, next_ch["seq"])) if next_ch else ""}"',
            "---",
            "",
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(fm) + body_md + "\n")

    # book index
    idx_path = os.path.join(BOOKS_DIR, f"{slug}-index.md")
    lines = [
        "---",
        "layout: book_index",
        f'title: "{fm_escape(book["title"])}"',
        f'book_slug: "{slug}"',
        f'genre: "{fm_escape(book["genre"])}"',
        f'author: "박종호"',
        f'release_date: {book.get("release_date", "")}',
        f'permalink: /brunchbook/{slug}/',
        "---",
        "",
        "## 목차",
        "",
    ]
    current_part = None
    for ch in chapters:
        if ch["part"] and ch["part"] != current_part:
            current_part = ch["part"]
            lines.append(f"\n**{html_escape(current_part)}**\n")
        lines.append(f'- [{ch["seq"]:02d}. {html_escape(ch["title"])}]({{{{ "/brunchbooks/{slug}/{ch["seq"]:02d}/" | relative_url }}}})')
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return len(chapters)


if __name__ == "__main__":
    total = 0
    for fn in sorted(os.listdir(DATA_DIR)):
        book = json.load(open(os.path.join(DATA_DIR, fn), encoding="utf-8"))
        n = build_book(book)
        total += n
        print(book["slug"], n)
    print("TOTAL", total)
