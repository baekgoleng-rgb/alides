"""Wikimedia Commons에서 비유 그림·영상 찾기/받기 (자유 라이선스만).

검색:  python commons.py search "galton board" [--n 10] [--video]
받기:  python commons.py get "File:Galton_box.jpg" <저장 폴더> [--name galton.jpg]
       영상(webm/ogv)은 480p로 받아 mp4(H.264)로 변환. --crop W:H:X:Y(높이 480 화면 기준)로 검은 여백 잘라내기

받은 파일마다 <저장 폴더>/credits.json 에 출처 문구를 기록 → 슬라이드 photo(credit=...)에 그대로 사용.
라이선스가 CC BY / CC BY-SA / CC0 / 퍼블릭 도메인이 아니면 받지 않음 (NC·ND·저작권 표시 파일 제외)
"""
import argparse, json, os, re, subprocess, sys, time, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "lecture-slides-skill/1.0 (educational slide preparation)"
FREE = re.compile(r"^(CC BY(-SA)? [\d.]+|CC0|Public domain|PD.*)$", re.I)


def get_json(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return json.load(r)


def download(url, path, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
                data = r.read()
            if not data.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
                open(path, "wb").write(data); return True
        except Exception as e:
            print("  retry:", e)
        time.sleep(3 * (k + 1))   # 위키미디어는 연속 요청을 막으므로 쉬었다가 재시도
    return False


def info(titles, width=1280):
    d = get_json({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
                  "iiprop": "url|size|mime|extmetadata", "iiurlwidth": width,
                  "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription"})
    out = []
    for p in d["query"]["pages"].values():
        if "imageinfo" not in p:
            continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        clean = lambda k: re.sub(r"<[^>]+>", "", m.get(k, {}).get("value", "")).strip()
        out.append({"title": p["title"], "url": ii["url"], "thumb": ii.get("thumburl"), "mime": ii.get("mime"),
                    "size": f'{ii.get("width")}x{ii.get("height")}', "license": clean("LicenseShortName"),
                    "artist": clean("Artist")[:80], "desc": clean("ImageDescription")[:120]})
    return out


def search(q, n, video):
    d = get_json({"action": "query", "list": "search", "srsearch": q + (" filetype:video" if video else " filetype:bitmap"),
                  "srnamespace": 6, "srlimit": n})
    titles = [h["title"] for h in d["query"]["search"]]
    for f in info(titles) if titles else []:
        ok = "OK " if FREE.match(f["license"]) else "NO "
        print(f'{ok}{f["title"]} | {f["size"]} | {f["license"]} | {f["artist"]}\n     {f["desc"]}')


def get(title, outdir, name=None, crop=None):
    os.makedirs(outdir, exist_ok=True)
    f = info([title if title.startswith("File:") else "File:" + title])[0]
    if not FREE.match(f["license"]):
        sys.exit(f'라이선스 "{f["license"]}" → 수업 자료에 자유롭게 쓸 수 없어 받지 않음')
    is_video = f["mime"].startswith("video")
    base = name or re.sub(r"[^\w.-]", "_", f["title"][5:])
    if is_video:
        orig = f["url"].split("?")[0]   # API가 붙이는 utm 꼬리 제거
        src = orig.replace("/commons/", "/commons/transcoded/", 1) + "/" + orig.rsplit("/", 1)[1] + ".480p.vp9.webm"
        tmp = os.path.join(outdir, "_tmp.webm")
        if not download(src, tmp, tries=2) and not download(orig, tmp):
            sys.exit("다운로드 실패")
        import imageio_ffmpeg
        mp4 = os.path.join(outdir, os.path.splitext(base)[0] + ".mp4")
        # 원본 해상도와 상관없이 높이 480으로 맞춘 뒤 자르므로 --crop 좌표는 480p 화면 기준
        vf = ["-vf", "scale=-2:480" + (f",crop={crop},scale=trunc(iw/2)*2:trunc(ih/2)*2" if crop else "")]
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", tmp, *vf,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", mp4], check=True)
        os.remove(tmp); path = mp4
    else:
        path = os.path.join(outdir, base)
        # 섬네일은 위키미디어가 정한 폭만 허용 → API가 준 thumburl 사용, 실패 시 원본
        if not (f["thumb"] and download(f["thumb"], path)) and not download(f["url"], path):
            sys.exit("다운로드 실패")
    kind = "영상" if is_video else "사진"
    credit = f'{kind}: {f["artist"]}, {f["license"]}, Wikimedia Commons'
    cj = os.path.join(outdir, "credits.json")
    credits = json.load(open(cj, encoding="utf-8")) if os.path.exists(cj) else {}
    credits[os.path.basename(path)] = {"credit": credit, "source": "https://commons.wikimedia.org/wiki/" + f["title"].replace(" ", "_")}
    json.dump(credits, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", path, "|", credit)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--n", type=int, default=10); s.add_argument("--video", action="store_true")
    g = sub.add_parser("get"); g.add_argument("title"); g.add_argument("outdir"); g.add_argument("--name"); g.add_argument("--crop")
    a = ap.parse_args()
    search(a.query, a.n, a.video) if a.cmd == "search" else get(a.title, a.outdir, a.name, a.crop)
