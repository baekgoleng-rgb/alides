"""예시: 04 정규분포 (교과서 개념 1·2) 강의 슬라이드 13장.

python deck.py <work 폴더> <출력 pptx>
  - <work>/media : 영상(anims.py 결과)과 인터넷 사진·영상(없으면 아래 MEDIA 목록대로 자동으로 받음)
  - <work>/fig   : 정적 그래프 PNG
이후 apply_anims.py <출력 pptx> <work>/media --poster galton.mp4=14000

새 단원을 만들 때 이 파일을 복사해 구조(표지 → 학습목표 → 생각 열기 → 비유 → 개념 → 예제 → 요약 → 퀴즈 → 정답 → 출처)와
애니메이션 거는 방식을 참고하고, 내용·그림은 해당 단원에 맞게 새로 작성
"""
import os, subprocess, sys
import numpy as np
from scipy.stats import norm
SCRIPTS = "C:/Users/Administrator/Desktop/alides/.claude/skills/lecture-slides/scripts"
sys.path.insert(0, SCRIPTS)
from slidekit import Deck, mpl_setup, save_fig, formula_png, trim_edges, load_credits, C, NAVY, BL, OR, MUTE
from pptx.enum.text import PP_ALIGN

WORK, OUT = sys.argv[1], sys.argv[2]
FIG, MEDIA = os.path.join(WORK, "fig"), os.path.join(WORK, "media")
plt = mpl_setup()

# ---------- 인터넷 비유 그림 (Wikimedia Commons, 자유 라이선스) ----------
MEDIA_SRC = {  # 파일명: (Commons 제목, 추가 옵션)
    "bell.png": ("File:Brass Gremlin Bell.png", []),
    "resistors.jpg": ("File:Carbon and ceramic resistors of different power ratings.jpg", []),
    "target.jpg": ("File:Archery Arrows in Paper Target.jpg", []),
    "galton.mp4": ("File:Galton box.webm", ["--crop", "360:480:247:0"]),   # 양옆 검은 여백 제거
}
for fn, (title, extra) in MEDIA_SRC.items():
    if not os.path.exists(os.path.join(MEDIA, fn)):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "commons.py"), "get", title, MEDIA, "--name", fn, *extra], check=True)
CR = load_credits(MEDIA)
bell = trim_edges(os.path.join(MEDIA, "bell.png"))

# ---------- AI 생성 영상·이미지 (Google Flow, 2026-10-20 생성 → media/flow_*) ----------
CR_AI_V = "AI 생성 영상: Google Flow (Omni 1.1 Flash)"
CR_AI_I = "AI 생성 이미지: Google Flow (Nano Banana 2.1)"
AI_W, AI_H = 1376, 768   # Flow 이미지 크기 (16:9 근사)

# ---------- 정적 그래프 ----------
def pdf_axes(figsize=(9, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    return fig, ax

x = np.linspace(-4, 4, 400); y = norm.pdf(x)
fig, ax = pdf_axes()
ax.plot(x, y, color=C.BLUE, lw=3); ax.fill_between(x, y, color=C.BLUE, alpha=.08)
ax.axvline(0, ymax=.95, color=C.GRAY, ls="--")
ax.annotate("", xy=(1, .242), xytext=(0, .242), arrowprops=dict(arrowstyle="<->", color=C.ORANGE, lw=2.5))
ax.text(.5, .255, r"$\sigma$", color=C.ORANGE, fontsize=24, ha="center")
ax.set_xticks([0]); ax.set_xticklabels([r"$m$"], fontsize=22)
f_pdf = save_fig(fig, f"{FIG}/pdf.png")

fig, ax = pdf_axes((10, 5))
ax.plot(x, y, color=C.BLUE, lw=3); ax.fill_between(x, y, color=C.BLUE, alpha=.15)
ax.axvline(0, ymax=.95, color=C.GRAY, ls="--"); ax.plot(0, norm.pdf(0), "o", color=C.RED, ms=9)
ax.text(.15, .405, "① 최댓값  " + r"$\frac{1}{\sqrt{2\pi}\,\sigma}$", fontsize=17, color=C.RED)
ax.text(-.12, .02, "② 대칭축 x = m", fontsize=15, color=C.GRAY, rotation=90, ha="right")
ax.text(.15, .03, "③ 넓이 = 1", fontsize=17, color=C.BLUE, weight="bold")
ax.annotate("④ x축에 한없이 가까워지는 곡선", xy=(3.3, .004), xytext=(1.9, .17), fontsize=15, color=C.GREEN,
            arrowprops=dict(arrowstyle="->", color=C.GREEN, lw=2))
ax.set_xticks([0]); ax.set_xticklabels([r"$m$"], fontsize=22); ax.set_ylim(0, .45)
f_prop = save_fig(fig, f"{FIG}/prop.png")

fig, ax = pdf_axes((8, 3.6))
x2 = np.linspace(-3, 7, 500)
ax.plot(x2, norm.pdf(x2, 1, 1.3), color=C.RED, lw=3); ax.plot(x2, norm.pdf(x2, 3.6, .7), color=C.BLUE, lw=3)
ax.text(-1.4, .12, "A", fontsize=22, color=C.RED); ax.text(5.1, .2, "B", fontsize=22, color=C.BLUE); ax.set_xticks([])
f_quiz = save_fig(fig, f"{FIG}/quiz.png")

f_def = formula_png(r"$f(x)=\frac{1}{\sqrt{2\pi}\,\sigma}\,e^{-\frac{(x-m)^2}{2\sigma^2}}$", f"{FIG}/def.png")
f_zdef = formula_png(r"$f(z)=\frac{1}{\sqrt{2\pi}}\,e^{-\frac{z^2}{2}}$", f"{FIG}/zdef.png")

# 예제용 레이어: 바탕 그림 + 구간별 색칠 그림을 같은 좌표로 저장 → 슬라이드에서 겹쳐 놓고 차례로 wipe
EXP = [(-4, 2), (-1, 3)]
LAYERS = {"a0": (0, -4, 0), "a1": (0, 0, 2), "b0": (1, -1, 0), "b1": (1, 0, 3)}
def ex_fig(layer=None):
    fig = plt.figure(figsize=(14, 4.2))
    axs = [fig.add_axes([.04 + k * .5, .14, .42, .72]) for k in range(2)]   # 축 위치 고정 (tight 금지)
    for k, ax in enumerate(axs):
        ax.set_xlim(-4, 4); ax.set_ylim(0, .45)
        if layer is None:
            a, b = EXP[k]
            ax.plot(x, y, color=C.BLUE, lw=3); ax.axvline(0, ymax=.95, color=C.GRAY, ls="--")
            ax.set_title([r"$P(Z\leq 2)$", r"$P(-1\leq Z\leq 3)$"][k], fontsize=20)
            ax.set_yticks([]); ax.spines["left"].set_visible(False)
            ax.set_xticks([v for v in (a, 0, b) if v > -4])
        else:
            ax.axis("off")
            panel, lo, hi = LAYERS[layer]
            if panel == k:
                xa = np.linspace(lo, hi, 200)
                ax.fill_between(xa, norm.pdf(xa), color=[C.GREEN, C.ORANGE][hi > 0], alpha=.45)
    return save_fig(fig, f"{FIG}/ex_{layer or 'base'}.png", tight=False)
f_ex_base = ex_fig(); f_ex = {k: ex_fig(k) for k in LAYERS}

# ---------- 슬라이드 ----------
d = Deck(tag="04 정규분포")

d.cover("확률과 통계 · Ⅲ. 통계", "04  정규분포", "자연·공학 데이터의 기본 모양, 종 모양 곡선",
        image=bell, credit=CR["bell.png"],
        notes="오늘의 주제: 정규분포. 종(bell)처럼 생긴 곡선이라 영어로 bell curve라고도 부른다는 점 소개")

s = d.slide("인트로: 쇠구슬이 그리는 곡선",
            notes="Google Flow로 만든 AI 영상, 슬라이드 진입 시 자동 재생(8초, 소리 없음). 공장 속 거대한 갈톤 보드에서 쇠구슬이 쌓이며 만드는 모양에 주목. "
                  "질문 순서: 가장 많이 쌓인 곳, 양 끝으로 갈수록 줄어드는 높이. 실제 실험이 아닌 AI 생성 장면이라는 점 안내, 실제 갈톤 보드 영상은 뒤 비유 슬라이드에서 확인")
d.video(s, "flow_intro.mp4", .5, 1.35, 8.9, 5.0)
d.text(s, .5, 6.4, 8.9, .3, CR_AI_V, 10, MUTE); d.credits.append(CR_AI_V)
d.text(s, 9.8, 1.5, 3.3, .6, "생각해 볼 질문", 20, BL, True)
for i, ln in enumerate(["가장 많이 쌓인 곳은?", "양 끝으로 갈수록?"]):
    d.anim(s, d.text(s, 9.8, 2.2 + i * .8, 3.3, .7, ln, 20))
d.anim(s, d.text(s, 9.8, 3.8, 3.3, 1.1, ["가운데 높고", "양옆 낮은 대칭 모양"], 20, OR, True))
d.anim(s, d.boxed(s, 9.7, 5.2, 3.3, 1.1, "오늘의 주제: 정규분포", 19))

s = d.slide("학습목표", notes="이번 시간 목표 3가지 소개. 클릭마다 하나씩 등장. 표준정규분포표 읽기까지가 오늘의 범위. 오른쪽 그림: 버니어 캘리퍼스로 축 지름을 재는 장면, 오늘 다룰 측정값 자료의 예")
for i, g in enumerate(["정규분포의 뜻과 기호 N(m, σ²)", "평균 m, 표준편차 σ에 따른 곡선 모양 변화", "표준정규분포표를 이용한 확률 계산"]):
    d.anim(s, d.boxed(s, .6, 1.7 + i * 1.6, 8.1, 1.2, [(f"{i+1}   ", BL, True), (g, NAVY, False)], 21, PP_ALIGN.LEFT))
d.photo(s, os.path.join(MEDIA, "flow_caliper.jpg"), 9.0, 2.2, credit=CR_AI_I, w=4.0)
d.text(s, 9.0, 2.2 + 4.0 * AI_H / AI_W + .4, 4.0, .9, ["같은 규격 부품의 지름 측정", "→ 조금씩 다른 측정값"], 16, MUTE)

s = d.slide("생각 열기: 저항 10000개의 저항값",
            notes="100 Ω 저항 10000개의 측정값. 영상 자동 재생: 계급의 크기 2 → 1 → 0.5 → 0.25 Ω으로 줄어드는 히스토그램, 마지막에 그려지는 주황색 곡선이 오늘 배울 정규분포 곡선")
d.photo(s, os.path.join(MEDIA, "resistors.jpg"), .5, 1.45, 3.9, CR["resistors.jpg"])
d.video(s, "hist.mp4", 3.7, 1.35, 9.2, 3.83)
d.anim(s, d.text(s, .6, 5.75, 12.2, 1.4, ["계급의 크기가 작을수록 좌우 대칭인 종 모양 곡선에 가까워지는 히스토그램",
                                         "강수량, 키, 부품 치수, 측정 오차 등 많은 자료에서 나타나는 현상"], 22))

s = d.slide("비유: 갈톤 보드(Galton board)",
            notes="공이 핀을 만날 때마다 왼쪽·오른쪽 중 하나로 튕기는 장치. 공 하나하나는 예측 불가능하지만 많이 모이면 종 모양. 측정 오차도 여러 작은 오차가 더해진 결과라 같은 원리라는 연결")
d.video(s, "galton.mp4", 1.0, 1.35, 3.6, 4.8)
d.text(s, .6, 6.2, 4.4, .5, CR["galton.mp4"], 10, MUTE); d.credits.append(CR["galton.mp4"])
for i, ln in enumerate(["핀마다 왼쪽·오른쪽 무작위 선택", "작은 우연이 여러 번 더해진 결과",
                        "가운데에 많이, 양 끝에 적게 쌓이는 공", "→ 종 모양 = 정규분포"]):
    d.anim(s, d.text(s, 5.4, 1.6 + i * .9, 7.5, .8, ln, 24, OR if i == 3 else NAVY, i == 3))
d.anim(s, d.boxed(s, 5.3, 5.3, 7.4, 1.2, "공학의 측정 오차 = 여러 작은 오차의 합 → 정규분포", 20))

s = d.slide("공학 속 정규분포",
            notes="클릭마다 사례 하나씩 등장. 왼쪽: 오실로스코프의 흔들리는 파형, 열잡음 등 여러 작은 잡음이 더해진 전압. 오른쪽: 생산라인 검사 카메라와 치수 분포 모니터, 같은 규격 부품의 치수 차이. "
                  "두 사례 모두 갈톤 보드처럼 작은 우연 요인의 합이라는 공통점. 두 그림 모두 Google Flow AI 생성 이미지")
PW = 5.9; PH = PW * AI_H / AI_W
for i, (fn, head, sub) in enumerate([("flow_scope.jpg", "신호 잡음", "흔들리는 전압 측정값"),
                                     ("flow_qc.jpg", "부품 치수 검사", "생산라인의 치수 분포")]):
    x0 = .6 + i * 6.3
    d.anim(s, d.photo(s, os.path.join(MEDIA, fn), x0, 1.35, credit=CR_AI_I, w=PW))
    d.anim(s, d.text(s, x0, 1.35 + PH + .4, PW, 1.0, [head, sub], 20, NAVY, True), "fade", "with")
d.anim(s, d.boxed(s, .6, 6.25, 12.2, .9, "공통점: 여러 작은 우연 요인이 더해진 값 → 종 모양 분포", 21))

s = d.slide("정규분포의 정의",
            notes="식 자체의 암기보다 m(중심 위치), σ(퍼진 정도) 두 역할의 이해가 핵심. 예: 평균 5, 표준편차 2인 정규분포는 N(5, 2²)이며, 괄호 안 두 번째 값이 분산이라는 점 주의")
d.box(s, .7, 1.5, 6.3, 4.6)
d.text(s, 1.0, 1.7, 5.8, .6, "정의", 22, BL, True)
d.text(s, 1.0, 2.3, 5.8, .9, "실수 전체에서 정의된 연속확률변수 X의 확률밀도함수", 20)
d.pic(s, f_def, 1.1, 3.2, w=4.4)
d.anim(s, d.text(s, 1.0, 4.3, 5.8, 1.6, ["→ X의 확률분포: 정규분포", "→ 기호: N(m, σ²)  (m: 평균, σ: 표준편차)"], 20, NAVY, True))
d.anim(s, d.pic(s, f_pdf, 7.3, 1.9, w=5.6), "wipe")
d.text(s, .7, 6.4, 12, .6, "N: normal distribution(정규분포)의 첫 글자", 16, MUTE)

s = d.slide("m과 σ에 따른 곡선의 변화",
            notes="영상 자동 재생. 왼쪽: σ가 커지면 낮고 넓게, 작아지면 높고 뾰족하게. 오른쪽: m이 바뀌면 모양은 그대로 위치만 이동. 과녁 비유: 화살이 중심 근처에 촘촘히 모인 궁수 = σ가 작은 상태, 공정에서는 품질이 고른 공정")
d.video(s, "shape.mp4", .4, 1.35, 9.0, 3.9)
d.photo(s, os.path.join(MEDIA, "target.jpg"), 9.8, 1.35, 3.2, CR["target.jpg"])
d.anim(s, d.text(s, 9.7, 4.95, 3.5, .9, ["비유: 중심에 모인 화살", "= σ가 작은 상태"], 15, OR, True))
for i, msg in enumerate(["σ ↑ : 낮고 넓게 퍼진 곡선", "m 변화 : 모양 유지, 위치만 이동"]):
    d.anim(s, d.boxed(s, .7 + i * 4.6, 6.0, 4.4, 1.0, msg, 17))

s = d.slide("정규분포 곡선의 성질",
            notes="오른쪽 목록이 클릭마다 하나씩 등장. 그림의 번호와 대응. 특히 ③ 전체 넓이 1은 모든 확률밀도함수의 공통 성질이며, 확률 = 넓이라는 연결고리")
d.pic(s, f_prop, .4, 1.4, w=7.6)
for i, ln in enumerate(["① x = m에서 최댓값", "② x = m에 대해 대칭인 종 모양", "③ 곡선과 x축 사이의 넓이 = 1",
                        "④ x축이 점근선", "⑤ σ ↑ → 낮고 넓게 퍼진 곡선", "⑥ m 변화 → 대칭축만 이동"]):
    d.anim(s, d.text(s, 8.2, 1.6 + i * .62, 5.0, .55, ln, 20))
d.photo(s, bell, 2.0, 5.6, 1.5, CR["bell.png"])
d.text(s, 3.5, 6.1, 4, .5, "← 종(bell) 모양 곡선의 유래", 15, MUTE)

s = d.slide("표준정규분포 N(0, 1)",
            notes="평균 0, 표준편차 1인 특별한 정규분포. 확률변수는 보통 Z로 표기. 영상: z가 0에서 1.23까지 커지며 쌓이는 넓이와 확률 값. 표에서 행은 소수 첫째 자리까지(1.2), 열은 소수 둘째 자리(0.03). 교과서 156쪽 표준정규분포표 함께 확인")
d.box(s, .7, 1.5, 5.6, 2.6)
d.text(s, 1.0, 1.65, 5.2, .6, "평균 0, 표준편차 1인 정규분포", 21, BL, True)
d.pic(s, f_zdef, 1.1, 2.4, w=3.6)
d.text(s, 1.0, 3.35, 5.2, .6, "확률 P(0 ≤ Z ≤ z) = 색칠한 부분의 넓이", 18)
d.video(s, "area.mp4", 6.7, 1.4, 6.2, 3.41)
d.text(s, .7, 4.4, 6, .6, "표준정규분포표 읽는 법", 21, NAVY, True)
d.anim(s, d.table(s, .7, 5.0, 6.2, 1.9, [["z", "0.00", "…", "0.03"], ["⋮", "", "", "⋮"], ["1.2", "…", "→", "0.3907"], ["⋮", "", "", ""]],
                  highlight={(2, 3)}))
d.anim(s, d.text(s, 7.2, 5.4, 5.8, 1.2, ["행: 1.2  /  열: 0.03", "→ P(0 ≤ Z ≤ 1.23) = 0.3907"], 20, OR, True))

s = d.slide("예제: 표준정규분포표로 확률 구하기",
            notes="클릭 순서: (1) 왼쪽 절반 넓이 0.5 → 0~2 구간 넓이 → 계산. (2) −1~0 구간 → 0~3 구간 → 계산. 음수 구간은 대칭으로 양수 구간으로 변환. 넓이 그림을 먼저 그린 뒤 표 찾기 습관화")
L, T, W = 1.0, 1.25, 11.3
d.pic(s, f_ex_base, L, T, w=W)
for col, (key, lines) in enumerate([("a", ["(1) P(Z ≤ 2)", "= 0.5 + P(0 ≤ Z ≤ 2)", "= 0.5 + 0.4772 = 0.9772"]),
                                    ("b", ["(2) P(−1 ≤ Z ≤ 3)", "= P(0 ≤ Z ≤ 1) + P(0 ≤ Z ≤ 3)", "= 0.3413 + 0.4987 = 0.8400"])]):
    x0 = 1.2 + col * 6.0
    d.text(s, x0, 5.05, 5.8, .5, lines[0], 19, NAVY, True)
    d.anim(s, d.pic(s, f_ex[key + "0"], L, T, w=W), "wipe", "click")
    d.anim(s, d.pic(s, f_ex[key + "1"], L, T, w=W), "wipe", "after")
    d.anim(s, d.text(s, x0, 5.65, 5.8, .5, lines[1], 19), "fade", "after")
    d.anim(s, d.text(s, x0, 6.25, 5.8, .5, lines[2], 19, OR, True), "fade", "click")

s = d.slide("핵심 요약", notes="다음 시간 예고: 일반 정규분포 N(m, σ²)를 표준정규분포로 바꾸는 표준화, Z = (X − m)/σ")
for i, (k, v) in enumerate([("정규분포", "평균 m, 표준편차 σ인 종 모양 분포, 기호 N(m, σ²)"), ("모양", "σ는 퍼짐 정도, m은 대칭축의 위치"),
                            ("넓이", "곡선 아래 전체 넓이 1, 구간의 넓이 = 확률"), ("표준정규분포", "N(0, 1), 표준정규분포표로 P(0 ≤ Z ≤ z) 계산")]):
    d.anim(s, d.boxed(s, .9, 1.55 + i * 1.3, 11.5, 1.05, [(f"{k}    ", BL, True), (v, NAVY, False)], 21, PP_ALIGN.LEFT))

s = d.slide("확인 퀴즈", notes="풀이 시간 3분. 1번은 그림만으로 판단, 2·3번은 표준정규분포표 사용")
d.text(s, .8, 1.5, 6.5, 1.5, ["Q1. 오른쪽 두 정규분포 곡선 A, B", "      평균의 대소와 표준편차의 대소 비교"], 20)
d.pic(s, f_quiz, 7.2, 1.3, w=5.6)
d.text(s, .8, 4.0, 12, .7, "Q2. P(Z ≤ −1.96)의 값  (단, P(0 ≤ Z ≤ 1.96) = 0.4750)", 20)
d.text(s, .8, 5.0, 12, .7, "Q3. P(|Z| ≤ 2.58)의 값  (단, P(0 ≤ Z ≤ 2.58) = 0.4951)", 20)

s = d.slide("확인 퀴즈 정답", notes="클릭마다 정답 하나씩 공개. Q2, Q3의 1.96과 2.58은 이후 신뢰구간(95%, 99%)에서 다시 등장하는 중요한 값")
for i, ln in enumerate(["Q1.  평균: A < B (오른쪽에 있는 B의 대칭축)  /  표준편차: A > B (더 낮고 넓은 A)",
                        "Q2.  P(Z ≤ −1.96) = 0.5 − P(0 ≤ Z ≤ 1.96) = 0.5 − 0.4750 = 0.0250",
                        "Q3.  P(|Z| ≤ 2.58) = 2 × P(0 ≤ Z ≤ 2.58) = 2 × 0.4951 = 0.9902"]):
    d.anim(s, d.text(s, .8, 1.7 + i * 1.0, 12, .7, ln, 21))

d.credits_slide(("그래프·애니메이션: 직접 제작 (Python matplotlib)", "AI 영상·이미지 생성일: 2026-10-20"))
d.save(OUT)
