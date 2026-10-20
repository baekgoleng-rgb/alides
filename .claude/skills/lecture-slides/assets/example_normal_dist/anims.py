"""예시: 04 정규분포 단원의 MP4 애니메이션 3개.  python anims.py <work 폴더>  → <work>/media/*.mp4

패턴: FuncAnimation + 매 프레임 ax.clear() 후 다시 그리기.
bbox_inches='tight'가 적용되지 않으므로 subplots_adjust로 여백을 직접 잡아 축 글자가 잘리지 않게 함
"""
import os, sys
import numpy as np
from scipy.stats import norm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from slidekit import mpl_setup, C

plt = mpl_setup(16)
from matplotlib.animation import FuncAnimation, FFMpegWriter

OUT = os.path.join(sys.argv[1], "media"); os.makedirs(OUT, exist_ok=True)
FPS = 25

def write(fig, fn, frames, name):
    FuncAnimation(fig, fn, frames=frames).save(
        os.path.join(OUT, name), dpi=150,
        writer=FFMpegWriter(fps=FPS, bitrate=2500, extra_args=["-pix_fmt", "yuv420p"]))
    plt.close(fig); print(name, frames / FPS, "s")

# 1) 계급의 크기를 줄여 가는 히스토그램 → 정규분포 곡선
data = np.random.default_rng(7).normal(100, 2, 10000)
widths, HOLD, DRAW, END = [2, 1, 0.5, 0.25], 40, 50, 30
fig, ax = plt.subplots(figsize=(12, 5)); fig.subplots_adjust(left=.08, right=.98, top=.95, bottom=.14)
xs = np.linspace(92, 108, 400)
def hist_frame(i):
    ax.clear()
    w = widths[min(i // HOLD, len(widths) - 1)]
    ax.hist(data, bins=np.arange(92, 108.01, w), density=True, color=C.BLUE, alpha=.75, edgecolor="white")
    ax.set_xlim(92, 108); ax.set_ylim(0, .24)
    ax.set_xlabel("저항값 (Ω)"); ax.set_ylabel("상대도수 / 계급의 크기")
    ax.text(92.3, .215, f"계급의 크기  {w} Ω", fontsize=22, color=C.BLUE, weight="bold")
    k = i - HOLD * len(widths)
    if k >= 0:
        n = min(len(xs), int(len(xs) * (k + 1) / DRAW))
        ax.plot(xs[:n], norm.pdf(xs[:n], 100, 2), color=C.ORANGE, lw=4)
        if k >= DRAW:
            ax.text(103.2, .17, "종 모양 곡선", fontsize=24, color=C.ORANGE, weight="bold")
write(fig, hist_frame, HOLD * len(widths) + DRAW + END, "hist.mp4")

# 2) σ와 m의 변화 (왼쪽 σ, 오른쪽 m, 점선은 기준 N(0,1))
fig, axs = plt.subplots(1, 2, figsize=(12, 5.2))
x, T = np.linspace(-6, 8, 600), 200
sig = np.clip(1 + .9 * np.sin(np.linspace(0, 2 * np.pi, T)), .55, 2)
mus = 2 * (1 - np.cos(np.linspace(0, 2 * np.pi, T)))
def shape_frame(i):
    for a in axs:
        a.clear(); a.set_yticks([]); a.spines["left"].set_visible(False); a.set_ylim(0, .75)
    a, b = axs
    a.plot(x, norm.pdf(x), color=C.GRAY, ls="--", lw=1.5); a.plot(x, norm.pdf(x, 0, sig[i]), color=C.RED, lw=4)
    a.set_xlim(-6, 6); a.set_title(r"$m=0$ 고정", fontsize=20)
    a.text(-5.6, .66, rf"$\sigma = {sig[i]:.2f}$", fontsize=26, color=C.RED)
    b.plot(x, norm.pdf(x), color=C.GRAY, ls="--", lw=1.5); b.plot(x, norm.pdf(x, mus[i], 1), color=C.GREEN, lw=4)
    b.axvline(mus[i], ymax=.55, color=C.GREEN, ls=":", lw=2)
    b.set_xlim(-4, 8); b.set_title(r"$\sigma=1$ 고정", fontsize=20)
    b.text(-3.6, .66, rf"$m = {mus[i]:.2f}$", fontsize=26, color=C.GREEN)
write(fig, shape_frame, T, "shape.mp4")

# 3) 넓이 P(0 ≤ Z ≤ z)가 쌓이며 확률 값이 함께 변함
fig, ax = plt.subplots(figsize=(8, 4.4))
z = np.linspace(-4, 4, 400)
zt = np.concatenate([np.linspace(0, 1.23, 60), np.full(40, 1.23)])
def area_frame(i):
    ax.clear(); ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.set_ylim(0, .48)
    ax.plot(z, norm.pdf(z), color=C.BLUE, lw=3)
    zz = np.linspace(0, zt[i], 100)
    ax.fill_between(zz, norm.pdf(zz), color=C.ORANGE, alpha=.6)
    ax.axvline(zt[i], ymax=.85, color=C.ORANGE, lw=2)
    ax.set_xticks([0, round(zt[i], 2)]); ax.set_xticklabels(["0", f"{zt[i]:.2f}"], fontsize=15)
    ax.text(1.55, .3, rf"$P(0\leq Z\leq {zt[i]:.2f})$" + f"\n= {norm.cdf(zt[i]) - .5:.4f}", fontsize=20, color=C.ORANGE)
write(fig, area_frame, len(zt), "area.mp4")
