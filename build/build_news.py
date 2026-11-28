#!/usr/bin/env python3
# NEWS ページ生成（Tumblr NEWS投稿の年表を移植）
import html, os

from dataload import load_years
from common import (CSS_DARK_COMMON, CSS_FOOTER_A, CSS_FOOTER_RULE,
                    CSS_HEAD, CSS_NAV, CSS_SNS, FOOTER_HTML, NAV_HTML,
                    YEARJS, esc, navjs, style_tag)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_site"))


# (日付, 本文, リンク先ファイル or None) — 本文は NEWS 投稿の原文どおり
# データは load_years() が返す：data/news.yaml の手動エントリ（リリース告知
# 以外）に、公開リリースから自動生成した告知を日付順にマージしたもの
# （旧: この場所にリテラル定義）
NAVJS = navjs()

YEARS = load_years()

CSS = (
    CSS_HEAD
    + '  .card { width:100%; max-width:560px; background:var(--glass);\n    -webkit-backdrop-filter:blur(14px) saturate(1.2); backdrop-filter:blur(14px) saturate(1.2);\n    border:1px solid var(--line); border-radius:20px;\n    box-shadow:0 12px 34px rgba(40,50,60,.22), inset 0 1px 0 rgba(255,255,255,.65); padding:10px 22px 18px; }\n  .year { font-size:11px; letter-spacing:.3em; color:var(--accent); font-weight:600; margin:10px 0 4px;\n    position:sticky; top:8px; z-index:5; }\n  .year span { display:inline-block; width:64px; box-sizing:border-box; text-align:center; padding:5px 0 5px .3em; border-radius:10px;\n    background:transparent; border:1px solid transparent; box-shadow:none;\n    transition:background .25s ease, box-shadow .25s ease; }\n  .year.stuck span { background:rgba(255,255,255,.65);\n    -webkit-backdrop-filter:blur(14px) saturate(1.2); backdrop-filter:blur(14px) saturate(1.2);\n    box-shadow:0 2px 8px rgba(40,50,60,.10); }\n  .item { display:flex; gap:12px; padding:7px 0; border-bottom:1px solid var(--line-dark); font-size:13.5px; }\n  .item:last-child { border-bottom:none; }\n  .item .d { color:var(--muted); font-size:12px; width:44px; flex:none; padding-top:2px; }\n  .item .d .dm { display:inline-block; width:15px; text-align:right; }\n  .item .d .dd { display:inline-block; width:15px; text-align:left; }\n  .item a { color:var(--ink); text-decoration:underline; text-underline-offset:3px; }\n  .item a:hover { color:var(--accent); }\n'
    + CSS_FOOTER_RULE
    + CSS_SNS
    + CSS_FOOTER_A
    + CSS_NAV
    + CSS_DARK_COMMON
    + '    .year.stuck span { background:rgba(42,49,56,.65); box-shadow:0 2px 8px rgba(0,0,0,.35); }\n  }\n'
)

NAV = NAV_HTML

body = []
for year, items in YEARS:
    body.append(f'<section class="ygrp"><div class="year"><span>{year}</span></div>')
    for d, text, link in items:
        t = f'<a href="{link}.html">{esc(text)}</a>' if link else esc(text)
        if '/' in d:
            mm, dd = d.split('/', 1)
            dhtml = (f'<span class="dm">{esc(mm)}</span>/'
                     f'<span class="dd">{esc(dd)}</span>')
        else:
            dhtml = esc(d)
        body.append(f'<div class="item"><span class="d">{dhtml}</span><span>{t}</span></div>')
    body.append('</section>')

doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>NEWS — rummy records</title>
{style_tag(CSS)}
</head>
<body>{NAV}
  <a class="label" href="index.html">rummy records</a>
  <div class="sub">NEWS</div>
  <div class="card">
    {''.join(body)}
  </div>
{FOOTER_HTML}{NAVJS}{YEARJS}
</body>
</html>
"""
path = os.path.join(OUT, "news.html")
with open(path, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", path)
