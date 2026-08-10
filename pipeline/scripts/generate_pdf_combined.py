# -*- coding: utf-8 -*-
import os, json
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                 Spacer, PageBreak, Image as RLImage)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

base = os.path.dirname(__file__)
DATA_DIR = os.path.join(base, "full_data")
IMG_DIR = os.path.join(base, "images")
OUT_DIR = os.path.join(base, "output")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_DIR = r"C:\Windows\Fonts"
FONT_REG = "HANBatang"
FONT_BOLD = "HANBatang-Bold"
pdfmetrics.registerFont(TTFont(FONT_REG, os.path.join(FONT_DIR, "HANBatang.ttf")))
pdfmetrics.registerFont(TTFont(FONT_BOLD, os.path.join(FONT_DIR, "HANBatangB.ttf")))

# 신국판 (Korean standard trade size)
PAGE_W, PAGE_H = 152 * mm, 225 * mm
MARGIN_L, MARGIN_R = 20 * mm, 20 * mm
MARGIN_T, MARGIN_B = 25 * mm, 28 * mm
AUTHOR = "박종호"

FULL_ORDER = ["mypicturedairy", "mypicturedairy2", "momochihama", "myhawaii", "ohashi",
              "tium", "v-meditation", "grit2success", "sosohan", "beautifuldays"]

VOLUMES = [
    {"title": "다시 틈사이로 1", "books": FULL_ORDER[0:4], "start_no": 1},
    {"title": "다시 틈사이로 2", "books": FULL_ORDER[4:10], "start_no": 5},
]

COPYRIGHT_LINES = [
    ("발행일", "2026년 9월 1일"),
    ("지은이", "박종호"),
    ("출판사", "퍼플"),
    ("", ""),
    ("출판등록", "제300-2012-167호 (2012년 09월 07일)"),
    ("주  소", "서울시 종로구 종로1가 1번지"),
    ("대표전화", "1544-1900"),
    ("홈페이지", "www.kyobobook.co.kr"),
]

DEDICATION = "아름다운 시절을 함께해준\n사랑하는 이들에게 드립니다."

# ---------- styles ----------
style_body = ParagraphStyle("body", fontName=FONT_REG, fontSize=10.6,
                             leading=18.5, alignment=TA_JUSTIFY, spaceAfter=10, firstLineIndent=14)
style_quote = ParagraphStyle("quote", fontName=FONT_REG, fontSize=10.0,
                              leading=17, alignment=TA_JUSTIFY, spaceAfter=10,
                              leftIndent=24, rightIndent=12, textColor=colors.HexColor("#555555"))
style_title_cover = ParagraphStyle("title_cover", fontName=FONT_BOLD, fontSize=27,
                                    alignment=TA_CENTER, leading=36)
style_author_cover = ParagraphStyle("author_cover", fontName=FONT_BOLD, fontSize=15,
                                     leading=20, alignment=TA_CENTER)
style_url_cover = ParagraphStyle("url_cover", fontName=FONT_REG, fontSize=9.5,
                                  leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#999999"))
style_dedication = ParagraphStyle("dedication", fontName=FONT_REG, fontSize=13,
                                   leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#333333"))
style_toc_title = ParagraphStyle("toc_title", fontName=FONT_BOLD, fontSize=17, leading=22, spaceAfter=18)
style_toc_book = ParagraphStyle("toc_book", fontName=FONT_BOLD, fontSize=11.5, leading=20,
                                 textColor=colors.HexColor("#222222"), spaceBefore=10)
style_toc_chapter = ParagraphStyle("toc_chapter", fontName=FONT_REG, fontSize=9.8, leading=15.5, leftIndent=16)
style_copyright_title = ParagraphStyle("copyright_title", fontName=FONT_BOLD, fontSize=15,
                                        leading=20, alignment=TA_CENTER, spaceAfter=22)
style_copyright_line = ParagraphStyle("copyright_line", fontName=FONT_REG, fontSize=10,
                                       leading=17, alignment=TA_LEFT)
style_copyright_notice = ParagraphStyle("copyright_notice", fontName=FONT_REG, fontSize=9,
                                         leading=15.5, alignment=TA_LEFT, textColor=colors.HexColor("#555555"))
style_book_no = ParagraphStyle("book_no", fontName=FONT_REG, fontSize=12,
                                leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#999999"))
style_book_divider_title = ParagraphStyle("book_divider_title", fontName=FONT_BOLD, fontSize=22,
                                           leading=30, alignment=TA_CENTER, spaceBefore=8)
style_part_divider = ParagraphStyle("part_divider", fontName=FONT_BOLD, fontSize=16,
                                     alignment=TA_CENTER, leading=23)
style_chapter_no = ParagraphStyle("chapter_no", fontName=FONT_REG, fontSize=10, leading=14,
                                   alignment=TA_CENTER, textColor=colors.HexColor("#AAAAAA"), spaceAfter=6)
style_chapter_title = ParagraphStyle("chapter_title", fontName=FONT_BOLD, fontSize=16,
                                      leading=23, alignment=TA_CENTER, spaceAfter=8)
style_chapter_subtitle = ParagraphStyle("chapter_subtitle", fontName=FONT_REG, fontSize=10.5, leading=15,
                                         alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceAfter=18)


def esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class BookDoc(BaseDocTemplate):
    current_book_title = ""

    def build(self, flowables, **kwargs):
        self.current_book_title = ""
        return BaseDocTemplate.build(self, flowables, **kwargs)

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            text = flowable.getPlainText()
            if style_name == "book_title_toc":
                self.notify("TOCEntry", (0, text, self.page))
                self.current_book_title = text
            elif style_name == "chapter_title_toc":
                self.notify("TOCEntry", (1, text, self.page))


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_REG, 8.5)
    canvas.setFillColor(colors.HexColor("#AAAAAA"))
    canvas.drawCentredString(PAGE_W / 2, 12 * mm, str(canvas.getPageNumber()))
    if doc.current_book_title and doc.page > 4:
        canvas.drawCentredString(PAGE_W / 2, PAGE_H - 15 * mm, doc.current_book_title)
    canvas.restoreState()


def add_image(story, block, usable_w):
    fname = block.get("local_file")
    if not fname:
        return
    img_path = os.path.join(IMG_DIR, fname)
    if not os.path.exists(img_path):
        return
    try:
        with PILImage.open(img_path) as im:
            iw, ih = im.size
        max_w = usable_w
        max_h = 150 * mm
        w = max_w
        h = w * ih / iw
        if h > max_h:
            h = max_h
            w = h * iw / ih
        story.append(RLImage(img_path, width=w, height=h, hAlign="CENTER"))
        story.append(Spacer(1, 6 * mm))
    except Exception:
        pass


def build(title, book_slugs, start_no):
    out_path = os.path.join(OUT_DIR, f"{title}.pdf")
    doc = BookDoc(out_path, pagesize=(PAGE_W, PAGE_H), leftMargin=MARGIN_L, rightMargin=MARGIN_R,
                  topMargin=MARGIN_T, bottomMargin=MARGIN_B, title=title, author=AUTHOR)
    frame = Frame(MARGIN_L, MARGIN_B, PAGE_W - MARGIN_L - MARGIN_R, PAGE_H - MARGIN_T - MARGIN_B, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_footer)])

    usable_w = PAGE_W - MARGIN_L - MARGIN_R
    story = []

    # ---- title page ----
    story.append(Spacer(1, 65 * mm))
    story.append(Paragraph(esc(title), style_title_cover))
    story.append(Spacer(1, 60 * mm))
    story.append(Paragraph(esc(AUTHOR), style_author_cover))
    story.append(Paragraph("brunch.co.kr/@freeist", style_url_cover))
    story.append(PageBreak())

    # ---- dedication page ----
    story.append(Spacer(1, 95 * mm))
    for i, line in enumerate(DEDICATION.split("\n")):
        story.append(Paragraph(esc(line), style_dedication))
    story.append(PageBreak())

    # ---- table of contents ----
    story.append(Paragraph("목차", style_toc_title))
    toc = TableOfContents()
    toc.levelStyles = [style_toc_book, style_toc_chapter]
    toc.dotsMinLevel = 0
    story.append(toc)
    story.append(PageBreak())

    # ---- copyright page ----
    story.append(Spacer(1, 60 * mm))
    story.append(Paragraph(esc(title), style_copyright_title))
    for label, value in COPYRIGHT_LINES:
        if not label:
            story.append(Spacer(1, 6 * mm))
            continue
        story.append(Paragraph(f"{esc(label)}&nbsp;&nbsp;&nbsp;&nbsp;{esc(value)}", style_copyright_line))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(f"ⓒ {esc(AUTHOR)} 2026", style_copyright_line))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("본 책 내용의 전부 또는 일부를 재사용하려면<br/>반드시 저작권자의 동의를 받으셔야 합니다.",
                            style_copyright_notice))
    story.append(PageBreak())

    # ---- books ----
    for i, slug in enumerate(book_slugs):
        book_i = start_no + i
        book = json.load(open(os.path.join(DATA_DIR, f"{slug}.json"), encoding="utf-8"))

        # book divider page
        story.append(Spacer(1, 70 * mm))
        story.append(Paragraph(f"제{book_i}권", style_book_no))
        book_title_style = ParagraphStyle("book_title_toc", parent=style_book_divider_title)
        story.append(Paragraph(esc(book["title"]), book_title_style))
        story.append(PageBreak())

        current_part = None
        for ch in book["chapters"]:
            if ch["part"] and ch["part"] != current_part:
                if current_part is not None:
                    story.append(PageBreak())
                current_part = ch["part"]
                story.append(Spacer(1, 75 * mm))
                story.append(Paragraph(esc(current_part), style_part_divider))
                story.append(PageBreak())
            else:
                story.append(PageBreak())

            story.append(Paragraph(f"{ch['seq']:02d}", style_chapter_no))
            chapter_title_style = ParagraphStyle("chapter_title_toc", parent=style_chapter_title)
            story.append(Paragraph(esc(ch["title"]), chapter_title_style))
            if ch["subtitle"]:
                story.append(Paragraph(esc(ch["subtitle"]), style_chapter_subtitle))
            else:
                story.append(Spacer(1, 10 * mm))

            for block in ch["blocks"]:
                if block["type"] == "img":
                    add_image(story, block, usable_w)
                    continue
                text = block.get("text", "")
                if not text.strip():
                    continue
                is_quote = block["type"] == "quote"
                html_text = esc(text).replace("\n", "<br/>")
                story.append(Paragraph(html_text, style_quote if is_quote else style_body))

        if i < len(book_slugs) - 1:
            story.append(PageBreak())

    doc.multiBuild(story)
    return out_path


if __name__ == "__main__":
    for vol in VOLUMES:
        out = build(vol["title"], vol["books"], vol["start_no"])
        print("DONE", out)
