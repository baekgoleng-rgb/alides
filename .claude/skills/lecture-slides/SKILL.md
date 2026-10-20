---
name: lecture-slides
description: 교과서 PDF를 바탕으로 그림·애니메이션 중심의 수학/통계 강의자료(PowerPoint .pptx)를 만드는 작업 흐름. 교과서 페이지를 이미지로 읽고, 명사형 종결(개조식) 문체로 쓰고, matplotlib로 정확한 그래프와 MP4 애니메이션을 만들고, Wikimedia Commons에서 자유 라이선스 비유 사진·영상을 찾아 출처를 표기하고, PowerPoint 클릭 애니메이션까지 붙여 완성한다. "강의자료 만들어줘", "N단원/N회차 슬라이드", "수업 PPT", "교과서 ○○절로 자료", "샘플 한 장", "애니메이션 넣어줘", "비유 그림 찾아줘", 기존 강의 pptx 수정처럼 강의·수업 슬라이드와 관련된 요청이면 단원 이름만 말해도 반드시 이 스킬을 사용.
---

# 강의 슬라이드 제작

교과서 단원 하나를 **그림이 주인공인 강의 슬라이드(.pptx)** 로 바꾸는 작업 흐름입니다.
학생이 글을 읽는 대신 그림과 움직임으로 개념을 보게 하는 것이 목표이므로, 글은 짧은 명사형으로 줄이고
변화가 핵심인 개념은 영상으로, 단계가 있는 설명은 클릭마다 하나씩 보여 줍니다.

작업 폴더(프로젝트)의 `CLAUDE.md`에 수업 대상·문체·구성 규칙이 있으면 그것이 우선입니다. 먼저 읽으세요.

## 도구 (scripts/)

| 스크립트 | 역할 |
|---|---|
| `render_pdf.py` | 교과서 PDF → 페이지 PNG (`--contact`: 12쪽씩 썸네일 모음으로 단원 위치 찾기) |
| `slidekit.py` | 디자인 상수(색·글꼴), matplotlib 설정, `Deck` 배치 함수, 애니메이션 표시 |
| `commons.py` | Wikimedia Commons 검색(`search`)·받기(`get`). 자유 라이선스만 받고 `credits.json`에 출처 기록, 영상은 mp4로 변환 |
| `apply_anims.py` | pptx의 애니메이션 표시를 PowerPoint 실제 효과·영상으로 변환 (Windows PowerPoint 필요) |
| `export_preview.py` | 슬라이드 PNG·6장 모음 미리보기 + 슬라이드별 애니메이션 순서 출력 |
| `check_style.py` | 명사형으로 끝나지 않은 문장(~다, ~요, 마침표) 찾기 |

**완성 예시**: `assets/example_normal_dist/` (정규분포 13장, `anims.py` + `deck.py`). 새 단원은 이 두 파일을 복사해서 시작하면 구조·애니메이션 거는 법을 그대로 가져올 수 있습니다.

필요 패키지: `pip install python-pptx matplotlib scipy pymupdf pillow imageio-ffmpeg pywin32`.
Windows 콘솔 한글 출력 오류(cp949)를 피하려고 Python 실행 시 `PYTHONIOENCODING=utf-8`을 붙이세요.

## 작업 순서

### 1. 교과서 읽기
한국 교과서 PDF는 글꼴 인코딩 때문에 텍스트 추출이 외계어처럼 깨지는 경우가 많습니다. 텍스트 추출을 시도하지 말고 페이지를 이미지로 보세요.
```bash
python scripts/render_pdf.py <pdf 또는 폴더> <scratch>/pages --contact      # 단원·절 위치 찾기
python scripts/render_pdf.py <pdf> <scratch>/pages --pages 22-27            # 해당 쪽 읽기 → Read 도구로 PNG 보기
```
교과서의 용어·기호·예제 번호를 그대로 따릅니다. 학생이 교과서와 슬라이드를 오가며 볼 때 헷갈리지 않게 하기 위해서입니다.

### 2. 구성안
기본 순서 (CLAUDE.md에 다른 구성이 있으면 그것을 따름):
표지 → (복습) → 학습목표 → 생각 열기 → 비유 → 개념(정의 → 그림 → 성질) → 예제 → 핵심 요약 → 확인 퀴즈 3문항 → 정답 → 그림 출처

슬라이드마다 정하세요:
- **영상(MP4, 자동 재생)**: 값이 연속으로 변할 때 무엇이 바뀌는지가 핵심인 개념. 예: 계급 크기 줄이기, 모수(σ, m, n, p) 변화, 넓이·확률 누적, 표본 반복 추출, 대수의 법칙
- **클릭 등장**: 순서가 의미 있는 내용. 학습목표, 성질 목록, 풀이 단계, 요약, 퀴즈 정답
- **wipe(왼쪽부터 칠하기)**: 넓이·구간 색칠. 풀이 줄과 순서를 맞춤
- **정적 그림**: 정의 그림, 비교 그림처럼 한눈에 보는 것

교과서의 일상 예시는 수업 대상에 맞게 바꿉니다 (공대생이면 부품 치수·측정 오차·불량률·신호 잡음 등).

### 3. 문체: 명사형 종결
슬라이드 글과 발표자 노트 모두 명사로 끝냅니다. 슬라이드 본문은 마침표도 생략합니다.
- 좋음: "두 사건이 동시에 일어날 확률", "낮고 넓게 퍼진 곡선", "곡선과 x축 사이의 넓이 = 1"
- 나쁨: "~이다.", "~입니다", "~해요", "~한다", "퍼짐"(동사 명사형보다 "퍼진 곡선"처럼 명사로)
- 노트 예: "식 자체의 암기보다 m, σ 두 역할의 이해가 핵심. 다음 시간 예고: 표준화"

### 4. 비유 그림 찾기 (인터넷)
개념마다 실물 비유를 하나씩 찾습니다. 학생이 낯선 수식을 이미 아는 장면과 연결하게 해 주기 때문입니다.
예: 정규분포 → 종, 갈톤 보드 영상 / 표준편차 → 과녁에 모인 화살 / 이항분포 → 동전 던지기 / 대수의 법칙 → 주사위 / 표본 추출 → 국 간 보기
```bash
python scripts/commons.py search "galton board" --n 8          # OK/NO 로 라이선스 표시
python scripts/commons.py search "galton box" --video
python scripts/commons.py get "File:Galton box.webm" <work>/media --name galton.mp4 --crop 360:480:247:0
```
- 자유 라이선스(CC BY, CC BY-SA, CC0, 퍼블릭 도메인)만 사용합니다. 수업 자료는 배포·공유되므로 NC/ND나 일반 웹 이미지는 쓰지 않습니다. `commons.py`가 자동으로 거릅니다
- 검색어는 영어가 결과가 많습니다. 받은 뒤 반드시 Read로 사진을 직접 보고 쓸지 결정하세요 (제목만 보고 고르면 엉뚱한 사진이 섞임)
- 사진 아래 작은 출처(`d.photo(..., credit=CR[파일명])`) + 마지막 "그림 출처" 슬라이드에 자동으로 모입니다
- 영상의 검은 여백은 `--crop`(480p 화면 기준 W:H:X:Y)으로 자르고, 첫 화면이 검으면 `apply_anims.py --poster 파일명=밀리초`

### 5. 만들기
단원마다 작업 폴더를 만듭니다: `build/NN_주제/` (프로젝트 안에 두어야 나중에 고칠 수 있음)
```
build/04_정규분포/
├── anims.py   # 영상 → media/*.mp4
├── deck.py    # 정적 그림(fig/) + 슬라이드 → output/NN_주제.pptx
├── media/     # 영상, 인터넷 사진, credits.json
└── fig/
```
예시 파일 맨 위의 `sys.path.insert(...)`를 스킬의 `scripts` 절대 경로로 바꾸세요.
```bash
python build/NN_주제/anims.py build/NN_주제
python build/NN_주제/deck.py  build/NN_주제 output/NN_주제.pptx
python scripts/apply_anims.py output/NN_주제.pptx build/NN_주제/media [--poster galton.mp4=14000]
```
`apply_anims.py`는 deck.py가 새로 만든 파일에 **한 번만** 실행합니다 (두 번 실행하면 효과가 겹침). 고칠 때는 deck.py부터 다시 돌리세요. 대상 pptx가 PowerPoint에 열려 있으면 실패하니 닫아 달라고 하세요.

`slidekit.Deck` 핵심 사용법 (단위: 인치, 슬라이드 13.333 × 7.5):
```python
d = Deck(tag="04 정규분포")                 # style/에 .potx/.pptx 양식이 있으면 Deck(template=경로)
s = d.slide("제목", notes="명사형 노트")
d.anim(s, d.text(s, l, t, w, h, ["줄1", "줄2"], 22))        # 클릭마다 등장
d.anim(s, d.boxed(s, l, t, w, h, "상자 속 글", 20))
d.anim(s, d.pic(s, png, l, t, w=W), "wipe", "after")        # 앞 효과 끝나면 이어서
d.video(s, "hist.mp4", l, t, w, h)                          # 슬라이드 들어가면 자동 재생
d.photo(s, path, l, t, h, credit)                           # 사진 + 출처
d.credits_slide(); d.save(out)
```

### 6. 점검 (보여 주기 전에 반드시)
```bash
python scripts/check_style.py output/NN_주제.pptx
python scripts/export_preview.py output/NN_주제.pptx <scratch>/preview
```
`grid*.png`를 Read로 보고 겹침·잘림·줄바꿈을 확인합니다. 영상은 `imageio_ffmpeg`의 ffmpeg로 중간 프레임(`-ss 초 -frames:v 1`)을 뽑아 확인합니다. 고친 뒤 5단계부터 다시 실행하세요.

## 자주 생긴 문제와 해결
- **그래프 축 글자 잘림 (영상)**: FuncAnimation 저장에는 `bbox_inches="tight"`가 적용되지 않음 → `fig.subplots_adjust(...)`로 여백 지정
- **글자가 그래프 축 눈금과 겹침**: 그림 아래 글은 그림 하단에서 0.3인치 이상 띄우기
- **한글 줄바꿈**: 20pt 한글 한 글자 ≈ 0.28인치. 상자 폭 = 글자 수 × 0.28 + 여백 0.6 이상. 넘치면 글을 줄이거나 글자를 1~2pt 줄임
- **겹쳐 등장하는 레이어 그림이 어긋남**: 같은 `figsize` + `fig.add_axes([...])` 고정 위치 + `save_fig(..., tight=False)`, 슬라이드에서도 같은 위치·폭
- **배경 지운 PNG 가장자리 선**: `trim_edges(path)`
- **Wikimedia 다운로드 실패(HTML 오류 페이지)**: 임의 폭 섬네일 금지·연속 요청 차단 때문. `commons.py`가 API 섬네일 주소 사용 + 대기 후 재시도
- **수식**: 슬라이드 글자로 쓰면 분수·지수가 깨짐 → `formula_png(r"$...$", path)`로 그림 삽입

## 마무리 보고
사용자에게 알릴 것: 저장 위치, 슬라이드 목록(무엇이 영상/클릭/비유인지), 사용한 인터넷 자료와 링크, 교과서 예시를 바꾼 곳, 확인하지 못한 것(예: 실제 슬라이드 쇼 재생은 직접 확인 필요).
