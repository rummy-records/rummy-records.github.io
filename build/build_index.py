#!/usr/bin/env python3
# ディスコグラフィ（index.html）生成 — 履歴＋公開停止中の扱いを実装
import html, os

from common import (CSS_DARK_COMMON, CSS_FOOTER_A, CSS_FOOTER_RULE,
                    CSS_HEAD, CSS_NAV, CSS_SNS, FOOTER_HTML, NAV_HTML,
                    SITE_DESC, YEARJS, esc, head_meta, navjs, style_tag)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_site"))


# 一覧行・シャッフル試聴データは data/releases/ から導出する
# （旧: ROWS / BCIDS / FIRST のコード内蔵リテラル。二重管理を解消済み）
from dataload import first_track_label, load_catalog, load_index_rows

ROWS = load_index_rows()

IMGEXT = {}
for fn in os.listdir(os.path.join(OUT, "img")):
    base, ext = os.path.splitext(fn)
    IMGEXT[base] = ext

CSS = (
    CSS_HEAD
    + '  .card { width:100%; max-width:560px; background:var(--glass);\n    -webkit-backdrop-filter:blur(14px) saturate(1.2); backdrop-filter:blur(14px) saturate(1.2);\n    border:1px solid var(--line); border-radius:20px;\n    box-shadow:0 12px 34px rgba(40,50,60,.22), inset 0 1px 0 rgba(255,255,255,.65); padding:10px 18px; }\n  .year { font-size:11px; letter-spacing:.3em; color:var(--accent); font-weight:600; margin:10px 0 4px;\n    position:sticky; top:8px; z-index:5; padding-left:2px; }\n  .year span { display:inline-block; width:64px; box-sizing:border-box; text-align:center; padding:5px 0 5px .3em; border-radius:10px;\n    background:transparent; border:1px solid transparent; box-shadow:none;\n    transition:background .25s ease, box-shadow .25s ease; }\n  .year.stuck span { background:rgba(255,255,255,.65);\n    -webkit-backdrop-filter:blur(14px) saturate(1.2); backdrop-filter:blur(14px) saturate(1.2);\n    box-shadow:0 2px 8px rgba(40,50,60,.10); }\n  .row { display:flex; align-items:center; gap:12px; padding:9px 2px; border-bottom:1px solid var(--line-dark);\n    text-decoration:none; color:var(--ink); }\n  .row:last-child { border-bottom:none; }\n  a.row:hover .ttl { color:var(--accent); }\n  .row img { width:64px; height:64px; border-radius:10px; object-fit:cover; flex:none;\n    box-shadow:0 2px 6px rgba(40,50,60,.25); background:#9aa7b1; }\n  .row .ph { width:64px; height:64px; border-radius:10px; flex:none; background:rgba(120,130,138,.25);\n    border:1px dashed rgba(120,130,138,.5); }\n  .row .main { flex:1; min-width:0; }\n  .row .ttl { font-size:14px; font-weight:600; line-height:1.4; }\n  .row .art { font-size:12px; color:var(--muted); }\n  .row .side { margin-left:auto; flex:none; text-align:right; display:flex; flex-direction:column; gap:2px; }\n  .row .date { font-size:11px; color:var(--muted); }\n  .row .cat { font-size:10px; color:var(--muted); letter-spacing:.05em; }\n  .row.dead { opacity:.55; }\n  .row .stop { font-size:10px; border:1px solid rgba(120,130,138,.5); border-radius:20px; padding:1px 8px; color:#5c666e; flex:none; }\n'
    + CSS_FOOTER_RULE
    + CSS_SNS
    + CSS_FOOTER_A
    + CSS_NAV
    + '\n  .randwrap { text-align:center; margin:-8px 0 22px; }\n  .randbtn { display:inline-flex; align-items:center; gap:8px; padding:10px 22px; border-radius:999px;\n    background:rgba(255,255,255,.42); border:1px solid var(--line); color:var(--ink);\n    -webkit-backdrop-filter:blur(10px) saturate(1.2); backdrop-filter:blur(10px) saturate(1.2);\n    box-shadow:0 6px 18px rgba(40,50,60,.16), inset 0 1px 0 rgba(255,255,255,.65);\n    font-family:inherit; font-size:13px; font-weight:600; letter-spacing:.14em; cursor:pointer;\n    transition:background .15s ease, border-color .15s ease; }\n  .randbtn:hover { background:rgba(255,255,255,.62); border-color:var(--accent); }\n  .pwrap { display:grid; grid-template-rows:0fr; width:100%; max-width:560px; position:relative; z-index:3;\n    transition:grid-template-rows .48s cubic-bezier(.4,0,.2,1); }\n  .pwrap.open { grid-template-rows:1fr; }\n  .pclip { overflow:hidden; min-height:0; }\n  .pwrap.settled .pclip { overflow:visible; }\n  .pcard { background:var(--glass); margin-bottom:16px;\n    -webkit-backdrop-filter:blur(14px) saturate(1.2); backdrop-filter:blur(14px) saturate(1.2);\n    border:1px solid var(--line); border-radius:20px;\n    box-shadow:0 12px 34px rgba(40,50,60,.22), inset 0 1px 0 rgba(255,255,255,.65);\n    padding:16px 18px; opacity:0; transform:translateY(-14px);\n    transition:opacity .3s ease, transform .48s cubic-bezier(.4,0,.2,1); }\n  .pwrap.open .pcard { opacity:1; transform:translateY(0); }\n  .pcard .prow { display:flex; align-items:center; gap:14px; }\n  .pcard .prow img { width:72px; height:72px; border-radius:10px; object-fit:cover; flex:none;\n    box-shadow:0 2px 6px rgba(40,50,60,.25); background:#9aa7b1; }\n  .pcard iframe { flex:1; min-width:0; height:42px; border:0; display:block; }\n  .pcard .ptrack { margin-top:12px; font-size:13.5px; color:var(--ink); letter-spacing:.02em; }\n  .pcard .pbtns { display:flex; gap:10px; margin-top:14px; }\n  .pcard .pbtn { flex:1; display:flex; align-items:center; justify-content:center; gap:7px; text-align:center; padding:9px 10px; border-radius:10px;\n    background:rgba(255,255,255,.42); border:1px solid var(--line); color:var(--ink);\n    font-family:inherit; font-size:13px; font-weight:600; text-decoration:none; cursor:pointer;\n    transition:background .15s ease, border-color .15s ease; }\n  .pcard .pbtn:hover { background:rgba(255,255,255,.62); border-color:var(--accent); color:var(--accent); }\n'
    + CSS_DARK_COMMON
    + '    .year.stuck span { background:rgba(42,49,56,.65); box-shadow:0 2px 8px rgba(0,0,0,.35); }\n    .row img, .pcard .prow img { background:#39424B; }\n    .row .stop { color:#9AA5AD; border-color:rgba(154,165,173,.4); }\n    .randbtn { background:rgba(255,255,255,.07); box-shadow:0 6px 18px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.14); }\n    .randbtn:hover { background:rgba(255,255,255,.13); }\n    .pcard { box-shadow:0 12px 34px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.14); }\n    .pcard .pbtn { background:rgba(255,255,255,.07); }\n    .pcard .pbtn:hover { background:rgba(255,255,255,.13); }\n  }\n'
)

NAV = NAV_HTML


NAVJS = navjs()

import json as _json
_by_file = {r["file"]: r for r in load_catalog()}
_bc_entries = []
for _cat, _f, _title, _artist, _date, _dead in ROWS:
    if _f and _by_file[_f].get("bandcamp_id"):
        _e = {"f": _f, "t": _title, "a": _artist, "d": _date, "c": _cat,
              "id": _by_file[_f]["bandcamp_id"],
              "img": "img/" + _f + IMGEXT.get(_f, ".jpg")}
        _e["ft"] = first_track_label(_by_file[_f])
        _bc_entries.append(_e)
BC_JSON = _json.dumps(_bc_entries, ensure_ascii=False)

RAND_HTML = """
  <div class="randwrap"><button class="randbtn" id="randbtn" type="button" aria-expanded="false"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"></polyline><line x1="4" y1="20" x2="21" y2="3"></line><polyline points="21 16 21 21 16 21"></polyline><line x1="15" y1="15" x2="21" y2="21"></line><line x1="4" y1="4" x2="9" y2="9"></line></svg>シャッフル試聴</button></div>
  <div class="pwrap" id="pcard"><div class="pclip"><div class="pcard">
    <div class="prow">
      <iframe id="pframe" title="Bandcamp player" loading="lazy" seamless></iframe>
    </div>
    <div class="ptrack" id="ptrack"></div>
    <div class="pbtns">
      <a class="pbtn" id="ppage" href="#">この作品のページへ</a>
      <button class="pbtn" id="pagain" type="button"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 5l8.5 7L6 19z"/><rect x="16.4" y="5" width="2.6" height="14" rx="0.6"/></svg>もう一曲</button>
    </div>
  </div></div></div>
"""

RANDJS = """
<script>
  (function () {
    var BC = __BC_JSON__;
    var btn = document.getElementById('randbtn');
    var card = document.getElementById('pcard');
    if (!btn || !card || !BC.length) return;
    var frame = document.getElementById('pframe'), page = document.getElementById('ppage'),
        again = document.getElementById('pagain'), track = document.getElementById('ptrack');
    var last = -1, isOpen = false;
    function pick() {
      var i;
      do { i = Math.floor(Math.random() * BC.length); } while (BC.length > 1 && i === last);
      last = i;
      var r = BC[i];
      page.href = r.f + '.html';
      track.textContent = r.ft ? '\u266a ' + r.ft : '';
      frame.src = 'https://bandcamp.com/EmbeddedPlayer/album=' + r.id + '/size=small/bgcol=ffffff/linkcol=c67223/transparent=true/';
    }
    function openCard() {
      pick();
      isOpen = true;
      card.classList.add('open');
      setTimeout(function () { if (isOpen) card.classList.add('settled'); }, 540);
      btn.setAttribute('aria-expanded', 'true');
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    function closeCard() {
      isOpen = false;
      card.classList.remove('open');
      card.classList.remove('settled');
      frame.src = 'about:blank';
      btn.setAttribute('aria-expanded', 'false');
    }
    btn.addEventListener('click', function () { if (isOpen) closeCard(); else openCard(); });
    again.addEventListener('click', pick);
  })();
</script>
""".replace("__BC_JSON__", BC_JSON)

def row_html(r):
    cat, f, title, artist, date, dead = r
    if dead:
        return (f'<div class="row dead"><span class="ph"></span>'
                f'<span class="main"><span class="ttl">{esc(title)}</span><br><span class="art">{esc(artist)}</span></span>'
                f'<span class="side"><span class="date">{date}</span><span class="cat">{cat}</span></span></div>')
    img = f"img/{f}{IMGEXT.get(f, '.jpg')}"
    return (f'<a class="row" href="{f}.html"><img src="{img}" alt="">'
            f'<span class="main"><span class="ttl">{esc(title)}</span><br><span class="art">{esc(artist)}</span></span>'
            f'<span class="side"><span class="date">{date}</span><span class="cat">{cat}</span></span></a>')

body = []
year = None
for r in ROWS:
    y = r[4][:4]
    if y != year:
        if year is not None:
            body.append('</section>')
        body.append(f'<section class="ygrp"><div class="year"><span>{y}</span></div>')
        year = y
    body.append(row_html(r))
if year is not None:
    body.append('</section>')

html_doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>rummy records — Discography</title>
{head_meta("rummy records — Discography", SITE_DESC, "")}{style_tag(CSS)}
</head>
<body>{NAV}
  <a class="label" href="index.html">rummy records</a>
  <div class="sub">DISCOGRAPHY</div>{RAND_HTML}
  <div class="card">
    {''.join(body)}
  </div>
{FOOTER_HTML}{NAVJS}{YEARJS}{RANDJS}
</body>
</html>
"""
path = os.path.join(OUT, "index.html")
with open(path, "w", encoding="utf-8") as fh:
    fh.write(html_doc)
print("wrote", path)
