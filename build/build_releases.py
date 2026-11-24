#!/usr/bin/env python3
# rummy records リリースページ量産スクリプト（v8テンプレート準拠）
# データ出典：release-data-20261122.md（検証済み）／ store-link-inventory-20261122.md
import html, os

from dataload import load_releases
from common import (CSS_FOOTER_A, CSS_FOOTER_RULE, CSS_NAV,
                    CSS_RELEASE_DARK, CSS_RELEASE_MAIN,
                    CSS_RELEASE_SECTIONS, CSS_RELEASE_TRACKS,
                    CSS_SNS, FOOTER_HTML, MORPH_JS, NAV_HTML, esc,
                    style_tag)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_site"))
os.makedirs(OUT, exist_ok=True)

# CSS 本体は common.py の断片合成（フェーズ3準備で compact 書式に統一し統合）。
# 並びは旧リテラルと同一で、生成HTMLの差分は空白のみ（検証済み）。
CSS = (
    CSS_RELEASE_MAIN
    + CSS_NAV
    + CSS_RELEASE_TRACKS
    + CSS_FOOTER_RULE
    + CSS_SNS
    + CSS_FOOTER_A
    + CSS_RELEASE_SECTIONS
    + CSS_RELEASE_DARK
)

NAV = NAV_HTML

_JS_PRE = "\n<script>\n  (function () {\n    var navbtn = document.getElementById('navbtn');\n    var navpanel = document.getElementById('navpanel');\n    if (navbtn && navpanel) {\n      navbtn.addEventListener('click', function (e) {\n        e.stopPropagation();\n        var open = navpanel.classList.toggle('open'); mbMorph(open);\n        navbtn.setAttribute('aria-expanded', open ? 'true' : 'false');\n        navpanel.setAttribute('aria-hidden', open ? 'false' : 'true');\n      });\n      document.addEventListener('click', function (e) {\n        if (!navpanel.contains(e.target)) {\n          navpanel.classList.remove('open'); mbMorph(false);\n          navbtn.setAttribute('aria-expanded', 'false');\n          navpanel.setAttribute('aria-hidden', 'true');\n        }\n      });\n    }\n    var bar = document.getElementById('minibar');\n    var title = document.getElementById('pagetitle');\n    if (!bar || !title || !('IntersectionObserver' in window)) return;\n    var observer = new IntersectionObserver(function (entries) {\n      entries.forEach(function (entry) {\n        var show = !entry.isIntersecting && entry.boundingClientRect.top < 0;\n        bar.classList.toggle('visible', show);\n        bar.setAttribute('aria-hidden', show ? 'false' : 'true');\n      });\n    }, { threshold: 0 });\n    observer.observe(title);\n\n"
_JS_POST = '\n  })();\n</script>\n'
JS = _JS_PRE + MORPH_JS + _JS_POST

CHEV = '<span class="chev"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>'

STORE_DEFS = {
    "bandcamp":   ("Bandcamp", "bandcamp"),
    "spotify":    ("Spotify", "spotify"),
    "applemusic": ("Apple Music", "applemusic"),
    "youtubemusic": ("YouTube Music", "youtubemusic"),
    "amazonmusic": ("Amazon Music", "amazonmusic"),
    "soundcloud": ("SoundCloud", "soundcloud"),
    "youtube":    ("YouTube", "youtube"),
    "youtube_pv": ("YouTube（PV）", "youtube"),
}


DL_ICON = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M6.5 10.5L12 16l5.5-5.5"/><path d="M4 20h16"/></svg>'

def store_btn(key, url):
    if key == "download":
        return (f'<a class="store dl" href="{esc(url)}">'
                f'{DL_ICON}<span class="name">Free Download</span>{CHEV}</a>')
    name, icon = STORE_DEFS[key]
    src = "img/amazonmusic.svg" if key == "amazonmusic" else f"https://cdn.simpleicons.org/{icon}"
    cls = ' class="amzn"' if key == "amazonmusic" else ""
    if url is None:
        return (f'<div class="store dead" aria-disabled="true">'
                f'<img src="{src}"{cls} alt="" width="26" height="26">'
                f'<span class="name">{esc(name)}</span><span class="tag">配信停止中</span></div>')
    return (f'<a class="store" href="{esc(url)}">'
            f'<img src="{src}"{cls} alt="" width="26" height="26">'
            f'<span class="name">{esc(name)}</span>{CHEV}</a>')

def track_html(no, title, feat, artist, genre=None, note=None):
    t = esc(title)
    if feat:
        t += f' <span class="feat">feat. {esc(feat)}</span>'
    a = ''
    if artist or genre:
        g = f'<span class="tgenre">{esc(genre)}</span>' if genre else ''
        a = f'<div class="tartist">{esc(artist) if artist else ""}{g}</div>'
    n = f'<div class="tnote">{esc(note)}</div>' if note else ''
    return f'<div class="track"><span class="no">{no}</span><div><div class="tname">{t}</div>{a}{n}</div></div>'

def T(title, artist=None, feat=None, genre=None, note=None):
    # artist 文字列に " feat. " が含まれていたらタイトル側へ分離する
    if artist and feat is None and " feat. " in artist:
        artist, feat = artist.split(" feat. ", 1)
    return (title, feat, artist, genre, note)

# データは data/releases.yaml から読み込む（旧: この場所にリテラル定義）
RELEASES = load_releases()

def render(r):
    stores = "\n      ".join(store_btn(k, u) for k, u in r["stores"])
    if r.get("special"):
        globe = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.7 2.6 4 5.6 4 9s-1.3 6.4-4 9c-2.7-2.6-4-5.6-4-9s1.3-6.4 4-9z"/></svg>')
        if r.get("special_off"):
            stores += ('\n      <span class="store off" aria-disabled="true">'
                       + globe + '<span class="name">Special Site</span></span>')
        else:
            stores += ('\n      <a class="store" href="' + esc(r["special"]) + '">'
                       + globe + '<span class="name">Special Site</span>' + CHEV + '</a>')
    tracks = "\n      ".join(track_html(i + 1, *t) for i, t in enumerate(r["tracks"]))
    bonus = ""
    if r.get("bonus"):
        start = len(r["tracks"]) + 1
        b = "\n      ".join(track_html(start + i, *t) for i, t in enumerate(r["bonus"]))
        bonus = f'\n      <h2 class="bonus">{esc(r["bonus_title"])}</h2>\n      {b}'
    if r.get("note"):
        bonus += f'\n      <p class="note">{esc(r["note"])}</p>'
    meta_extra = f'<span>{esc(r["extra_meta"])}</span>' if r.get("extra_meta") else ""
    credits = f'\n    <p class="credits">{esc(r["credits"])}</p>' if r.get("credits") else ""
    license_html = ""
    if r.get("license") == "by-nc":
        license_html = ('\n    <p class="license"><img src="https://cdn.simpleicons.org/creativecommons" alt="" width="16" height="16">'
                        'この作品は <a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a> ライセンスで提供されています</p>')
    info = f'\n    <p class="credits">{esc(r["info"])}</p>' if r.get("info") else ""
    pre_html = ""
    tag_cls = "tagline"
    if r.get("pre"):
        parts = []
        for i, p in enumerate(r["pre"]):
            cls = "tagline" if i == 0 else "tagline cont"
            parts.append(f'\n    <p class="{cls}">{p}</p>')
        pre_html = "".join(parts)
        tag_cls = "tagline cont"
    sections_html = ""
    staff_html = ""
    rest_html = ""
    for sec in r.get("sections", []):
        kind, head, data = sec
        if kind == "staff":
            row_html = []
            for row in data:
                role, name = row[0], row[1]
                url = row[2] if len(row) > 2 else None
                nm = f'<a href="{esc(url)}">{esc(name)}</a>' if url else esc(name)
                row_html.append(f'<div class="srow"><span class="role">{esc(role)}</span><span class="sname">{nm}</span></div>')
            rows = "\n      ".join(row_html)
            block = f'\n    <div class="sect"><h2>{esc(head)}</h2>\n      {rows}\n    </div>'
            staff_html += block
            sections_html += block
        elif kind == "lyrics":
            items = "\n      ".join(
                f'<details class="lyr"><summary>{esc(t)}</summary><div class="lyric">{esc(x)}</div></details>'
                for t, x in data)
            block = f'\n    <div class="sect"><h2>{esc(head)}</h2>\n      {items}\n    </div>'
            rest_html += block
            sections_html += block
        elif kind == "embed":
            block = (f'\n    <div class="sect"><h2>{esc(head)}</h2>'
                              f'<div class="xfade"><iframe src="{esc(data)}" allow="autoplay" title="{esc(head)}"></iframe></div></div>')
            rest_html += block
            sections_html += block
    if r.get("license") == "by-nc" or r.get("credits_first"):
        staff_first, sections_after = staff_html, rest_html
    else:
        staff_first, sections_after = "", sections_html
    mini_artist = r.get("mini_artist", r["artist"])
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{esc(r['title'])} — rummy records</title>
{style_tag(CSS)}
</head>
<body>
  <div class="bg-glow" aria-hidden="true"><div class="blob"></div></div>
{NAV}

  <div class="minibar" id="minibar" aria-hidden="true">
    <div class="minibar-inner">
      <img class="thumb" src="{esc(r['art'])}" alt="">
      <div class="mtitle">{esc(r['title'])}<div class="martist">{esc(mini_artist)}</div></div>
    </div>
  </div>

  <a class="label" href="index.html">rummy records</a>

  <div class="card">
    <img class="cover" src="{esc(r['art'])}" alt="{esc(r['title'])} ジャケット">

    <h1 class="title" id="pagetitle">{esc(r['title'])}</h1>
    <p class="artist">{esc(r['artist'])}</p>
    <p class="meta"><span>{esc(r['cat'])}</span><span>{esc(r['date'])}</span>{meta_extra}</p>{credits}{info}

    <div class="stores">
      {stores}
    </div>

    <div class="tracks">
      <h2>TRACKS</h2>
      {tracks}{bonus}
    </div>

{staff_first}{pre_html}
    <p class="{tag_cls}">{r['tagline']}</p>{license_html}{sections_after}
  </div>

{FOOTER_HTML}
{JS}
</body>
</html>
"""

for r in RELEASES:
    path = os.path.join(OUT, r["file"] + ".html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(r))
    print("wrote", path)
print("done:", len(RELEASES), "pages")
