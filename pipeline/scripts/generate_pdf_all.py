# -*- coding: utf-8 -*-
import os, json
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
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

PAGE_W, PAGE_H = A5
MARGIN_L, MARGIN_R = 18 * mm, 18 * mm
MARGIN_T, MARGIN_B = 20 * mm, 22 * mm
AUTHOR = "박종호"

style_body = ParagraphStyle("body", fontName=FONT_REG, fontSize=10.3,
                             leading=17, alignment=TA_JUSTIFY, spaceAfter=9, firstLineIndent=13)
style_quote = ParagraphStyle("quote", fontName=FONT_REG, fontSize=9.8,
                              leading=16, alignment=TA_JUSTIFY, spaceAfter=9,
                              leftIndent=22, rightIndent=10, textColor=colors.HexColor("#555555"))
style_title_cover = ParagraphStyle("title_cover", fontName=FONT_BOLD, fontSize=24,
                                    alignment=TA_CENTER, leading=32)
style_genre_cover = ParagraphStyle("genre_cover", fontName=FONT_REG, fontSize=11,
                                    leading=15, alignment=TA_CENTER, textColor=colors.HexColor("#666666"))
style_author_cover = ParagraphStyle("author_cover", fontName=FONT_BOLD, fontSize=14,
                                     leading=18, alignment=TA_CENTER)
style_url_cover = ParagraphStyle("url_cover", fontName=FONT_REG, fontSize=9,
                                  leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#999999"))
style_toc_title = ParagraphStyle("toc_title", fontName=FONT_BOLD, fontSize=16, leading=21, spaceAfter=16)
style_toc_part = ParagraphStyle("toc_part", fontName=FONT_BOLD, fontSize=11.5, leading=16,
                                 textColor=colors.HexColor("#333333"), spaceBefore=10, spaceAfter=4)
style_toc_chapter = ParagraphStyle("toc_chapter", fontName=FONT_REG, fontSize=10.5, leading=16, leftIndent=14)
style_part_divider_base = ParagraphStyle("part_divider_base", fontName=FONT_BOLD, fontSize=18,
                                          alignment=TA_CENTER, leading=26)
style_chapter_no = ParagraphStyle("chapter_no", fontName=FONT_REG, fontSize=10, leading=14,
                                   alignment=TA_CENTER, textColor=colors.HexColor("#AAAAAA"), spaceAfter=6)
style_chapter_title_base = ParagraphStyle("chapter_title_base", fontName=FONT_BOLD, fontSize=17,
                                           leading=24, alignment=TA_CENTER, spaceAfter=8)
style_chapter_subtitle = ParagraphStyle("chapter_subtitle", fontName=FONT_REG, fontSize=10.5, leading=15,
                                         alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceAfter=18)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class BookDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            text = flowable.getPlainText()
            if style_name == "chapter_title_toc":
                self.notify("TOCEntry", (0, text, self.page))
            elif style_name == "part_divider_toc":
                self.notify("TOCEntry", (0, text, self.page))


def make_footer(title):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT_REG, 8)
        canvas.setFillColor(colors.HexColor("#AAAAAA"))
        canvas.drawCentredString(PAGE_W / 2, 10 * mm, str(canvas.getPageNumber()))
        if doc.page > 1:
            canvas.drawCentredString(PAGE_W / 2, PAGE_H - 12 * mm, title)
        canvas.restoreState()
    return draw


def build_book(book):
    title = book["title"]
    out_path = os.path.join(OUT_DIR, f"{title}.pdf")
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except PermissionError:
            out_path = os.path.join(OUT_DIR, f"{title} (수정판).pdf")
    doc = BookDoc(out_path, pagesize=A5, leftMargin=MARGIN_L, rightMargin=MARGIN_R,
                  topMargin=MARGIN_T, bottomMargin=MARGIN_B, title=title, author=AUTHOR)
    frame = Frame(MARGIN_L, MARGIN_B, PAGE_W - MARGIN_L - MARGIN_R, PAGE_H - MARGIN_T - MARGIN_B, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=make_footer(title))])

    story = []
    story.append(Spacer(1, 50 * mm))
    story.append(Paragraph(esc(title), style_title_cover))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(esc(book.get("genre", "")), style_genre_cover))
    story.append(Spacer(1, 55 * mm))
    story.append(Paragraph(esc(AUTHOR), style_author_cover))
    story.append(Paragraph("brunch.co.kr/@freeist", style_url_cover))
    story.append(PageBreak())

    story.append(Paragraph("목차", style_toc_title))
    toc = TableOfContents()
    toc.levelStyles = [style_toc_chapter]
    toc.dotsMinLevel = 0
    story.append(toc)
    story.append(PageBreak())

    current_part = None
    usable_w = PAGE_W - MARGIN_L - MARGIN_R
    for ch in book["chapters"]:
        if ch["part"] and ch["part"] != current_part:
            if current_part is not None:
                story.append(PageBreak())
            current_part = ch["part"]
            story.append(Spacer(1, 60 * mm))
            p_style = ParagraphStyle("part_divider_toc", parent=style_part_divider_base)
            story.append(Paragraph(esc(current_part), p_style))
            story.append(PageBreak())
        else:
            story.append(PageBreak())

        story.append(Paragraph(f"{ch['seq']:02d}", style_chapter_no))
        title_style = ParagraphStyle("chapter_title_toc", parent=style_chapter_title_base)
        story.append(Paragraph(esc(ch["title"]), title_style))
        if ch["subtitle"]:
            story.append(Paragraph(esc(ch["subtitle"]), style_chapter_subtitle))
        else:
            story.append(Spacer(1, 10 * mm))

        for block in ch["blocks"]:
            if block["type"] == "img":
                fname = block.get("local_file")
                if not fname:
                    continue
                img_path = os.path.join(IMG_DIR, fname)
                if not os.path.exists(img_path):
                    continue
                try:
                    with PILImage.open(img_path) as im:
                        iw, ih = im.size
                    max_w = usable_w
                    max_h = 130 * mm
                    w = max_w
                    h = w * ih / iw
                    if h > max_h:
                        h = max_h
                        w = h * iw / ih
                    story.append(RLImage(img_path, width=w, height=h, hAlign="CENTER"))
                    story.append(Spacer(1, 6 * mm))
                except Exception:
                    continue
                continue

            text = block.get("text", "")
            if not text.strip():
                continue
            is_quote = block["type"] == "quote"
            html_text = esc(text).replace("\n", "<br/>")
            story.append(Paragraph(html_text, style_quote if is_quote else style_body))

    doc.multiBuild(story)
    return out_path


if __name__ == "__main__":
    results = []
    errors = []
    for fn in sorted(os.listdir(DATA_DIR)):
        if fn == "drawer.json":
            continue
        book = json.load(open(os.path.join(DATA_DIR, fn), encoding="utf-8"))
        try:
            out = build_book(book)
            results.append(out)
        except Exception as e:
            errors.append(f"{fn}: {e}")
    with open(os.path.join(base, "pdf_gen_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n---ERRORS---\n" + "\n".join(errors))
    print("DONE", len(results), "ERRORS", len(errors))
