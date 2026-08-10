# 브런치 아카이브 파이프라인 (작업 이어하기용)

이 폴더는 GitHub Pages 사이트(`../`)를 만드는 데 쓰인 원본 데이터와 생성 스크립트입니다.
다른 기기/세션에서 이 저장소를 클론하면 그대로 이어서 작업할 수 있습니다.

## 폴더 구성

- `full_data/*.json` — 브런치북 9권 + 파일럿 1권(grit2success) + 서랍(drawer) 본문 데이터. 각 챕터의 title/subtitle/blocks(문단·인용·이미지)를 담고 있습니다.
- `magazines_data/*.json` — 매거진 4개(321편) 본문 데이터.
- `../assets/images/` — 이미지 원본(리사이즈, 최대 가로 1400px) 418장. 중복 저장을 피하려 여기 pipeline 폴더가 아니라 사이트의 assets 폴더에 그대로 둡니다. 스크립트를 새 환경에서 돌릴 때 `IMG_DIR` 경로를 `../assets/images`로 맞춰주세요.
- `scripts/` — 데이터 수집·문서 생성 스크립트 (아래 참고).
- `books_meta.json` — 브런치북 9권의 챕터 순서/파트 구성 메타데이터.
- `drafts_export.json` — 서랍 39편 원본 추출 결과(가공 전).

## 스크립트 역할

| 파일 | 역할 |
|---|---|
| `brunch_lib.py` | 브런치 페이지 HTML에서 astro-island JSON을 파싱하는 공용 라이브러리 |
| `fetch_all_books.py` | `books_meta.json` 기준으로 브런치북 9권을 브런치에서 재수집 |
| `fetch_magazines.py` | 매거진 4개를 API 페이지네이션으로 재수집 |
| `download_resize_images.py` | `full_data/*.json`의 이미지 URL을 내려받아 리사이즈, `local_file` 필드 추가 |
| `generate_docx_all.py` | 브런치북별 DOCX(단행본 스타일, A5) 생성 |
| `generate_pdf_all.py` | 브런치북별 PDF(단행본 스타일, A5) 생성 |
| `generate_pdf_combined.py` | 브런치북 1~10권을 신국판(152×225mm) 통합 출판용 PDF로 생성 (표지·헌사·목차·판권지 포함, 현재 2권 분할 설정) |
| `generate_md_all.py` | 브런치북 GitHub Pages용 markdown 생성 (`../_brunchbooks/`) |
| `generate_magazine_md.py` | 매거진 GitHub Pages용 markdown 생성 (`../_magazines/`) |
| `build_drafts_book.py` | `drafts_export.json` → `full_data/drawer.json` 변환 (서랍, 날짜순 정렬) |
| `book_data.py` / `convert_pilot.py` | 파일럿 브런치북(사업, 일단 시작하고 봅시다) 원본 데이터 및 통합 포맷 변환 |

## 재생성 방법

```bash
cd pipeline/scripts
python generate_pdf_combined.py   # 신국판 통합 PDF (다시 틈사이로 1/2)
python generate_pdf_all.py        # 권별 PDF
python generate_docx_all.py       # 권별 DOCX
python generate_md_all.py         # 브런치북 블로그 페이지
python generate_magazine_md.py    # 매거진 블로그 페이지
```

출력물은 `scripts/output/`, `scripts/../` 등 스크립트 상단의 `OUT_DIR` 설정을 따라갑니다 —
새 환경에서 돌릴 때는 각 스크립트 상단의 `base`, `DATA_DIR`, `OUT_DIR`, `SITE` 경로를
새 환경의 실제 폴더 구조에 맞게 확인해 주세요.

## ⚠️ 폰트 의존성 (중요)

PDF 생성 스크립트(`generate_pdf_all.py`, `generate_pdf_combined.py`)는
Windows 시스템 폰트 `C:\Windows\Fonts\HANBatang.ttf` / `HANBatangB.ttf`를 사용합니다.
(나눔명조는 한자 글리프가 없어서 한자가 깨지는 문제가 있었고, HANBatang으로 교체했습니다 — 59,330 글리프, 한자 포함.)

다른 OS(macOS/Linux)나 폰트가 없는 환경에서 이어서 작업할 경우:
1. 완전한 한자 글리프를 포함한 한국어 명조/바탕 계열 폰트를 구해서 `FONT_DIR` 경로를 그 폰트로 바꾸거나,
2. 폰트 파일을 이 저장소에 함께 커밋해 절대경로 대신 상대경로로 참조하도록 스크립트를 수정하세요.

DOCX(`generate_docx_all.py`)는 "Nanum Myeongjo"라는 폰트 *이름*만 문서에 저장하므로,
읽는 사람의 Word/한글에 해당 폰트가 없으면 자동으로 다른 폰트로 대체되어 열립니다(별도 임베딩 불필요).

## 최근 작업 이력 (참고)

1. 브런치북 10권(178화) + 서랍 39편 + 매거진 4개(321편) 수집, GitHub Pages 블로그 배포
2. 본문 추출 버그 수정 (스타일 적용된 텍스트 구간이 누락되던 문제)
3. 블로그 링크에 baseurl(`/brunch-archive/`) 누락 버그 수정
4. PDF 한자 깨짐(폰트 교체) + 제목/부제목 겹침(leading 누락) 버그 수정
5. 브런치북 1~10권 신국판 통합 출판용 PDF 제작 → 사용자 요청으로 2권 분할
   (「다시 틈사이로 1」= 1~4권, 「다시 틈사이로 2」= 5~10권), 각 권 독립 판권지 포함
