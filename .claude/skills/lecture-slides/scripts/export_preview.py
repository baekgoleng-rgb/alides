"""완성된 pptx 점검용: 슬라이드별 PNG와 6장씩 모은 미리보기, 슬라이드별 애니메이션 순서 출력.

python export_preview.py <deck.pptx> <출력 폴더> [--slides 3 5 9]

애니메이션은 이미지에 나타나지 않으므로(모든 도형이 보이는 최종 상태) 순서는 출력 목록으로 확인.
영상은 포스터 장면으로 보임
"""
import argparse, os
import win32com.client
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("pptx"); ap.add_argument("out")
ap.add_argument("--slides", nargs="*", type=int)
a = ap.parse_args()
out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)

TRIG = {1: "click", 2: "with", 3: "after"}
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(os.path.abspath(a.pptx), True, False, False)
try:
    nums = a.slides or list(range(1, pres.Slides.Count + 1))
    for i in nums:
        sl = pres.Slides(i)
        seq = sl.TimeLine.MainSequence
        steps = [f"{seq.Item(k).Shape.Name[:22]}({TRIG.get(seq.Item(k).Timing.TriggerType, '?')})"
                 for k in range(1, seq.Count + 1)]
        print(f"slide {i}: " + (", ".join(steps) if steps else "-"))
        sl.Export(os.path.join(out, f"s{i:02d}.png"), "PNG", 1600, 900)
finally:
    pres.Close(); app.Quit()

ims = [Image.open(os.path.join(out, f"s{i:02d}.png")).resize((800, 450)) for i in nums]
for k in range(0, len(ims), 6):
    g = Image.new("RGB", (1600, 1350), "white")
    for j, im in enumerate(ims[k:k + 6]):
        g.paste(im, ((j % 2) * 800, (j // 2) * 450))
    g.save(os.path.join(out, f"grid{k // 6}.png"))
print("preview grids:", out)
