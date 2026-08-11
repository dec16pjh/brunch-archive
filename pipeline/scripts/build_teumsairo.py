# -*- coding: utf-8 -*-
import re, os, json

base = os.path.dirname(__file__)
text = open(os.path.join(base, "teumsairo_text.txt"), encoding="utf-8").read()
pages_raw = re.split(r"===== PAGE (\d+) =====\n", text)[1:]
page_map = {}
for i in range(0, len(pages_raw), 2):
    page_map[int(pages_raw[i])] = pages_raw[i + 1]

# (title, start_page, part)
PHIL = "철학 에세이"
PROSE = "산문"
POEM = "시와 단상"

CHAPTERS = [
    ("철학과 '철학'", 10, PHIL),
    ("진퇴양란에 빠진 마음", 19, PHIL),
    ("'空과 깨달음'", 31, PHIL),
    ("섬을 이어주는 다리-共感", 35, PHIL),
    ("'있음'과 '앎'", 43, PHIL),
    ("剛三昧經論 중 本覺利品 읽기", 49, PHIL),
    ("'시여, 침을 뱉어라'", 56, PHIL),
    ("오외디푸스왕(王)을 읽고", 65, PHIL),
    ("채플(chapel)과 사과밥", 68, PHIL),
    ("소크라테스의 대화 중 (31a-e)", 75, PHIL),
    ("아리스토텔레스의 세상보기", 79, PHIL),
    ("플라톤은 왜 대화편을 썼을까?", 84, PHIL),
    ("두 시대의 충돌과 그 안의 여자, 魔女", 88, PHIL),
    ("이제 문제는 냉전세력이다", 96, PHIL),
    ("자연법은 무엇인가?", 108, PHIL),
    ("中國의 神化", 110, PHIL),
    ("세인트 클레어, 사람 사랑하는 일", 119, PHIL),
    ("「인간의 존엄과 인권」", 127, PHIL),
    ("자유와 평등은 어떠한 근거에서 정당화 될 수 있는가?", 140, PHIL),
    ("열린 마음과 귀기울임", 142, PHIL),
    ("유모어, 가벼움 들여다보기", 151, PROSE),
    ("정현종씨의 '마음에 이는 작은 폭풍'을 읽고", 160, PROSE),
    ("『논문작성법강의』", 162, PROSE),
    ("페데리코 가르시아 로르카", 166, PROSE),
    ("If I were a tree in 21th century", 176, POEM),
    ("시인이게 드리는 글", 178, POEM),
    ("새끼 고래 한 마리가 바다로 가는 길에 태공을 만나다", 182, POEM),
    ("공주와 시인", 184, POEM),
    ("모든 것", 186, POEM),
    ("사랑하는 일엔 이유가 없다", 187, POEM),
    ("山 오르며", 188, POEM),
    ("이 시간", 189, POEM),
    ("풍경", 190, POEM),
    ("그 길 끝에서", 191, POEM),
    ("길가에 앉아", 192, POEM),
    ("한국 근대 혁명사", 193, POEM),
    ("倩女1", 194, POEM),
    ("@시쓰기", 195, POEM),
    ("@시", 195, POEM),
    ("@나는 시를 써야한다", 196, POEM),
    ("틈 사이로", 201, POEM),
]

END_PAGE = 202  # exclusive; guestbook/comments section starts here, not part of formal TOC


def strip_page_number_lines(page_text):
    # remove ALL standalone page-number-only lines (each page starts with one)
    lines = page_text.split("\n")
    out = [l for l in lines if not l.strip().isdigit()]
    return "\n".join(out)


def get_raw_text(start_page, end_page):
    parts = []
    for p in range(start_page, end_page):
        if p in page_map:
            parts.append(strip_page_number_lines(page_map[p]))
    return "\n".join(parts)


def _norm(s):
    return (s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
             .replace("'", "").replace('"', "").replace("(", "").replace(")", "")
             .replace(",", "").replace(".", "").replace(" ", ""))


def remove_title_occurrence(raw, title):
    # remove the first standalone line matching the title (heading line)
    lines = raw.split("\n")
    key = _norm(title)
    for i, l in enumerate(lines):
        ln = _norm(l.strip())
        if ln and (ln == key or (len(key) > 6 and key[:10] in ln and len(ln) < len(key) + 8)):
            del lines[i]
            break
    return "\n".join(lines)


def to_paragraphs_prose(raw):
    # group by blank-line-separated blocks, join internal lines with space
    blocks = re.split(r"\n\s*\n+", raw)
    out = []
    for b in blocks:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if not lines:
            continue
        joined = " ".join(lines)
        joined = re.sub(r"\s+", " ", joined).strip()
        if joined:
            out.append(joined)
    return out  # list of paragraph strings


def to_lines_poem(raw):
    # preserve line breaks; collapse multiple blanks; strip page-number-only lines
    lines = [l.strip() for l in raw.split("\n")]
    # drop leading/trailing empties
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    out = []
    prev_blank = False
    for l in lines:
        if not l:
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(l)
            prev_blank = False
    return out  # list of lines, "" = stanza break


chapters_out = []
for i, (title, start, part) in enumerate(CHAPTERS):
    end = CHAPTERS[i + 1][1] if i + 1 < len(CHAPTERS) else END_PAGE
    if end <= start:
        end = start + 1
    raw = get_raw_text(start, end)
    raw = remove_title_occurrence(raw, title)

    blocks = []
    if part == POEM:
        lines = to_lines_poem(raw)
        # group into stanzas by blank-line markers, each stanza = one block, lines joined with \n
        stanza = []
        for l in lines:
            if l == "":
                if stanza:
                    blocks.append({"type": "p", "text": "\n".join(stanza)})
                    stanza = []
            else:
                stanza.append(l)
        if stanza:
            blocks.append({"type": "p", "text": "\n".join(stanza)})
    else:
        paras = to_paragraphs_prose(raw)
        for p in paras:
            blocks.append({"type": "p", "text": p})

    chapters_out.append({
        "seq": i + 1,
        "part": part,
        "no": None,
        "title": title,
        "subtitle": "",
        "date": None,
        "url": "",
        "blocks": blocks,
    })

book = {
    "title": "틈사이로",
    "genre": "틈사이로 (2001)",
    "author": "박종호",
    "release_date": "2001",
    "slug": "teumsairo2001",
    "chapters": chapters_out,
}

out_path = os.path.join(base, "full_data", "teumsairo2001.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(book, f, ensure_ascii=False, indent=2)

print("chapters:", len(chapters_out))
