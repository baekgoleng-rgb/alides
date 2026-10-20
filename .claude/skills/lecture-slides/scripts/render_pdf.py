"""교과서 PDF 페이지 → PNG.

한국 교과서 PDF는 글꼴 인코딩 때문에 텍스트 추출이 깨지는 경우가 많아(외계어처럼 나옴),
페이지를 이미지로 만들어 Read 도구로 직접 보는 방식이 정확함.

python render_pdf.py <pdf 또는 폴더> <출력 폴더> [--pages 22-27] [--dpi 90] [--contact]
  --contact : 전체를 작은 썸네일 모음(12쪽씩)으로 만들어 단원·절 위치를 빠르게 찾을 때 사용
"""
import argparse, glob, os
import pymupdf
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--pages", help="예: 22-27 (1부터 시작)")
ap.add_argument("--dpi", type=int, default=90)
ap.add_argument("--contact", action="store_true")
a = ap.parse_args()

src = a.src if a.src.lower().endswith(".pdf") else sorted(glob.glob(os.path.join(a.src, "*.pdf")))[0]
doc = pymupdf.open(src)
os.makedirs(a.out, exist_ok=True)
if a.pages:
    lo, _, hi = a.pages.partition("-")
    rng = range(int(lo), int(hi or lo) + 1)
else:
    rng = range(1, len(doc) + 1)
print(f"{os.path.basename(src)}: {len(doc)} pages")

if a.contact:
    thumbs = [Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
              for pm in (doc[i - 1].get_pixmap(dpi=30) for i in rng)]
    nums = list(rng)
    for k in range(0, len(thumbs), 12):
        part = thumbs[k:k + 12]; w, h = part[0].size
        g = Image.new("RGB", (w * 4, h * 3), "white")
        for j, im in enumerate(part):
            g.paste(im, ((j % 4) * w, (j // 4) * h))
        p = os.path.join(a.out, f"contact_p{nums[k]:03d}-{nums[k + len(part) - 1]:03d}.png")
        g.save(p); print(p)
else:
    for i in rng:
        p = os.path.join(a.out, f"p{i:03d}.png")
        doc[i - 1].get_pixmap(dpi=a.dpi).save(p); print(p)
