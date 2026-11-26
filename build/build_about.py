#!/usr/bin/env python3
# About us ページ生成（Tumblr の #about 投稿を移植）
import os

from common import (CSS_DARK_COMMON, CSS_FOOTER_A, CSS_FOOTER_RULE,
                    CSS_HEAD, CSS_NAV, CSS_SNS, FOOTER_HTML, NAV_HTML,
                    navjs, style_tag)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_site"))

CSS = (
    CSS_HEAD
    + '  .icon { width:92px; height:92px; display:block; margin:0 auto 20px; }\n  .card { width:100%; max-width:560px; background:var(--glass);\n    -webkit-backdrop-filter:blur(14px) saturate(1.2); backdrop-filter:blur(14px) saturate(1.2);\n    border:1px solid var(--line); border-radius:20px;\n    box-shadow:0 12px 34px rgba(40,50,60,.22), inset 0 1px 0 rgba(255,255,255,.65); padding:26px 26px 22px; }\n  .card p { font-size:14.5px; line-height:2.0; margin-bottom:18px; }\n  .card h2 { font-size:11px; letter-spacing:.3em; color:var(--accent); font-weight:600; margin:24px 0 8px; }\n  .card ul { list-style:none; }\n'
    + CSS_SNS
    + '  .card li { padding:6px 0; border-bottom:1px solid var(--line-dark); font-size:14px; }\n  .card li:last-child { border-bottom:none; }\n  .card a { color:var(--ink); text-decoration:underline; text-underline-offset:3px; }\n  .card a:hover { color:var(--accent); }\n  .card .role { color:var(--muted); font-size:12px; }\n'
    + CSS_FOOTER_RULE
    + CSS_FOOTER_A
    + CSS_NAV
    + CSS_DARK_COMMON
    + '    .icon { content:url("img/icon-white.png"); }\n  }\n'
)

NAV = NAV_HTML

NAVJS = navjs()

doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>About us — rummy records</title>
{style_tag(CSS)}
</head>
<body>{NAV}
  <a class="label" href="index.html">rummy records</a>
  <div class="sub">ABOUT US</div>
  <div class="card">
    <img class="icon" src="img/icon.png" alt="rummy records アイコン">
    <p>rummy records (ラミーレコーズ)<br>
    大阪大学 音楽制作サークル ラムレーズンのメンバーにより<br>
    2015年1月に設立された<br>
    ダンスミュージックを中心とする電子音楽専門ネットレーベル。</p>
    <p>クラブカルチャーに馴染みのないリスナーにも聞きやすく<br>
    トラックメイカーにとって新しい発見のある<br>
    コアでキャッチーな楽曲を発信する。</p>
    <h2>MEMBER</h2>
    <ul>
      <li><a href="https://x.com/nennen2010">Nennen</a> <span class="role">(Organizer)</span></li>
      <li><a href="https://twitter.com/zero_yon_nana">zero yon nana</a> <span class="role">(Co-organizer)</span></li>
      <li><a href="https://twitter.com/BSer_Lingi">BSer / Lingi</a></li>
      <li><a href="https://x.com/bnsk_kyuru">dusKape</a></li>
      <li><a href="https://twitter.com/nurumayu">nurumayu</a></li>
    </ul>
  </div>
{FOOTER_HTML}{NAVJS}
</body>
</html>
"""
path = os.path.join(OUT, "about.html")
with open(path, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", path)
