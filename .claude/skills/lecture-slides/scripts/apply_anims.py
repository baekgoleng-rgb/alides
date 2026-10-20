"""slidekit이 남긴 도형 이름(A순번|효과|시점)을 PowerPoint의 실제 애니메이션·영상으로 변환.

python apply_anims.py <deck.pptx> <영상 폴더> [--poster galton.mp4=14000 ...]

- PowerPoint(Windows, COM)가 필요. 대상 파일이 PowerPoint에 열려 있으면 실패하므로 먼저 닫을 것
- 같은 pptx에 두 번 실행하지 말 것: 영상 자리 표시가 이미 영상으로 바뀌어 있어 효과가 중복됨.
  항상 deck.py로 새로 만든 직후에 한 번만 실행
- --poster: 영상이 재생되기 전 보여줄 장면(ms). 첫 화면이 검은 영상에 사용
"""
import argparse, os
import win32com.client

EFFECT = {"fade": 10, "wipe": 22, "appear": 1}
TRIGGER = {"click": 1, "with": 2, "after": 3}
MEDIA_PLAY, DIR_LEFT = 83, 4

ap = argparse.ArgumentParser()
ap.add_argument("pptx"); ap.add_argument("media_dir")
ap.add_argument("--poster", nargs="*", default=[], help="파일명=밀리초")
a = ap.parse_args()
poster = {k: int(v) for k, v in (p.split("=") for p in a.poster)}

app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(os.path.abspath(a.pptx), False, False, False)
try:
    for slide in pres.Slides:
        marked = sorted((sh.Name, sh) for sh in slide.Shapes if sh.Name.startswith("A") and "|" in sh.Name)
        seq = slide.TimeLine.MainSequence
        for name, sh in marked:
            _, effect, trigger = name.split("|")
            if effect.startswith("video:"):
                fn = effect[6:]
                l, t, w, h = sh.Left, sh.Top, sh.Width, sh.Height
                sh.Delete()
                mv = slide.Shapes.AddMediaObject2(os.path.abspath(os.path.join(a.media_dir, fn)), False, True, l, t, w, h)
                mv.Name = "video " + fn
                if fn in poster:
                    mv.MediaFormat.SetDisplayPicture(poster[fn])
                seq.AddEffect(mv, MEDIA_PLAY, 0, TRIGGER[trigger])
                continue
            e = seq.AddEffect(sh, EFFECT[effect], 0, TRIGGER[trigger])
            e.Timing.Duration = .6 if effect == "wipe" else .4
            if effect == "wipe":
                e.EffectParameters.Direction = DIR_LEFT
    pres.Save()
    print("animations applied:", a.pptx)
finally:
    pres.Close(); app.Quit()
