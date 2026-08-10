# -*- coding: utf-8 -*-
import re, json, html as htmlmod

ISLAND_RE = re.compile(r'<astro-island[^>]*component-export="([^"]*)"[^>]*props="([^"]*)"', re.S)


def unwrap(v):
    if isinstance(v, list) and len(v) == 2 and v[0] == 0:
        return unwrap(v[1])
    if isinstance(v, dict):
        return {k: unwrap(val) for k, val in v.items()}
    if isinstance(v, list):
        return [unwrap(x) for x in v]
    return v


def find_islands(raw_html):
    out = []
    for m in ISLAND_RE.finditer(raw_html):
        export_name = m.group(1)
        props_raw = m.group(2)
        try:
            props = json.loads(htmlmod.unescape(props_raw))
        except Exception as e:
            continue
        out.append((export_name, unwrap(props)))
    return out


def extract_text(data_arr):
    """Recursively walk nested text/data/br nodes (styled spans nest another data array) and concatenate leaf text."""
    out = []
    for d in (data_arr or []):
        if d.get("type") == "br":
            out.append("\n")
        elif isinstance(d.get("text"), str):
            out.append(d["text"])
        elif isinstance(d.get("data"), list):
            out.append(extract_text(d["data"]))
    return "".join(out)


def parse_article_html(raw_html):
    """Return the unwrapped article dict from a chapter/article page."""
    for export_name, data in find_islands(raw_html):
        if "article" in data:
            article = data["article"]
            content_str = article.get("content")
            if isinstance(content_str, str):
                try:
                    article["content_parsed"] = json.loads(content_str)
                except Exception:
                    article["content_parsed"] = None
            return article
    return None


if __name__ == "__main__":
    import sys, os
    base = os.path.dirname(__file__)
    raw = open(os.path.join(base, sys.argv[1]), encoding="utf-8", errors="ignore").read()
    islands = find_islands(raw)
    with open(os.path.join(base, "islands_dump.json"), "w", encoding="utf-8") as f:
        json.dump([{"export": n, "keys": list(d.keys()) if isinstance(d, dict) else str(type(d))} for n, d in islands],
                   f, ensure_ascii=False, indent=2)
    print("islands:", [n for n, d in islands])
