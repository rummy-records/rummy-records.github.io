#!/usr/bin/env python3
"""data/ の YAML を読み込み、レンダラが期待する内部形式（タプル等）に戻すローダ。

リポジトリ配置（フェーズ3）版：
- リリースは data/releases/rmmyXXX.yaml の個別ファイル（Decap フォルダ
  コレクション対応）。公開停止4件も suspended: true で同フォルダに含む。
- NEWS は data/news.yaml 単一ファイルだが、持つのはリリース告知以外の
  エントリ（M3出展・イベント等）だけ。リリース告知は load_years() が
  公開リリースから自動生成して日付順にマージする。告知文は既定では
  「RMMY-XXX「タイトル」リリース」で、リリース側の任意項目で上書きできる：
  news_text（文面そのもの）、news_date（日付表示）、news_skip（生成しない）、
  news_after（同日の手動 NEWS より後に並べる）。
- 日付風文字列は YAML 上でクオートしてあるが、Decap が無クオートで
  書き戻した場合に datetime.date として読まれても ISO 文字列に戻す
  （防御的正規化）。
- 歌詞データ（旧 lyrics025.py）は各リリース YAML 内の sections に取り込み済み。
"""
import datetime
import glob
import os

import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DATA = os.path.join(ROOT, "data")
RELEASES_DIR = os.path.join(DATA, "releases")


def _fix(v):
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, dict):
        return {k: _fix(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_fix(x) for x in v]
    return v


def _load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return _fix(yaml.safe_load(f))


def _track(d):
    return (d["title"], d.get("feat"), d.get("artist"),
            d.get("genre"), d.get("note"))


def _section(s):
    kind, head = s["kind"], s["head"]
    if kind == "staff":
        rows = []
        for r in s["rows"]:
            if "url" in r:
                rows.append((r["role"], r["name"], r["url"]))
            else:
                rows.append((r["role"], r["name"]))
        return ("staff", head, rows)
    if kind == "lyrics":
        return ("lyrics", head, [(g["title"], g["text"]) for g in s["songs"]])
    if kind == "embed":
        return ("embed", head, s["url"])
    raise ValueError(f"unknown section kind: {kind}")


def _convert(r):
    d = {}
    for k, v in r.items():
        if k in ("tracks", "bonus"):
            d[k] = [_track(t) for t in v]
        elif k == "stores":
            d[k] = [(s["key"], s.get("url")) for s in v]
        elif k == "sections":
            d[k] = [_section(s) for s in v]
        else:
            d[k] = v
    return d


def load_catalog():
    """data/releases/ の全エントリ（公開停止含む）を内部形式で返す。

    ファイル名順（= 品番順）。各エントリは YAML の全キーに加え、
    元データに無い項目は含まれない（suspended / bandcamp_id 等は任意）。
    """
    out = []
    for path in sorted(glob.glob(os.path.join(RELEASES_DIR, "*.yaml"))):
        out.append(_convert(_load_yaml(path)))
    return out


def load_releases():
    """ページ生成対象（公開停止を除く）のリリース一覧。旧 RELEASES 相当。"""
    return [r for r in load_catalog() if not r.get("suspended")]


def load_index_rows():
    """ディスコグラフィ一覧の行データをリリースデータから導出する。

    旧 build_index.py の ROWS（コード内蔵）を置き換えるもの。
    並びは旧 ROWS と同じ「日付の新しい順、同日は品番の大きい順」。
    戻り値: (cat, file or None, title, artist, date, suspended) のリスト。
    """
    rows = []
    for r in load_catalog():
        dead = bool(r.get("suspended"))
        rows.append((r["cat"], None if dead else r["file"], r["title"],
                     r["artist"], r["date"], dead))
    rows.sort(key=lambda row: (row[4], row[0]), reverse=True)
    return rows


def first_track_label(release):
    """シャッフル試聴用の1曲目ラベルを1曲目のデータから導出する。

    旧 build_index.py の FIRST（コード内蔵）を置き換えるもの。
    規則: 「曲名 [feat. X] [— アーティスト]」（ある要素だけを連結）。
    全12件で旧 FIRST と一致することを検証済み。
    """
    title, feat, artist, _genre, _note = release["tracks"][0]
    label = title
    if feat:
        label += f" feat. {feat}"
    if artist:
        label += f" — {artist}"
    return label


def _news_date_tuple(s):
    """手動 NEWS の日付文字列 'M/DD' / 'MM/DD' を (月, 日) にする。空は None。"""
    if not s:
        return None
    m, d = str(s).split("/")
    return (int(m), int(d))


def _fmt_news_date(s):
    """NEWS の日付表示を 'M/D'（ゼロなし）に統一する。空・解釈不能はそのまま。"""
    if not s:
        return s
    try:
        t = _news_date_tuple(s)
    except Exception:
        return s
    if t is None:
        return s
    return f"{t[0]}/{t[1]}"


def _release_news_entry(r):
    """リリース1件から NEWS 告知エントリを生成する。

    戻り値: (年, (月, 日), 表示日付, 本文, リンク先, news_after か)。
    文面の既定は最新の形式「RMMY-XXX「タイトル」リリース」（タイトルのみ、
    スペースなし）。過去の表記ゆれはリリース側の news_text で再現する。
    """
    ymd = str(r["date"])  # YYYY-MM-DD（_fix で文字列化済み）
    m, d = int(ymd[5:7]), int(ymd[8:10])
    date_str = _fmt_news_date(r.get("news_date")) or f"{m}/{d}"
    text = r.get("news_text") or f'{r["cat"]}「{r["title"]}」リリース'
    return (ymd[:4], (m, d), date_str, text, r["file"],
            bool(r.get("news_after")))


def load_years():
    """旧 gen_news.py の YEARS と同形式のリストを返す。

    data/news.yaml の手動エントリ（リリース告知以外）を背骨にして、
    公開リリース（news_skip を除く）から自動生成した告知エントリを
    日付の新しい順に挿入する。同日の手動エントリとは原則「告知が先」
    （現行 NEWS の並びがそうなっている）で、リリース側に news_after が
    ある場合のみ手動エントリの後に置く。日付の無い手動エントリは
    挿入位置の判定から外し、元の位置関係を保つ。
    """
    manual = {}
    for y in _load_yaml(os.path.join(DATA, "news.yaml"))["years"]:
        manual[y["year"]] = [(_fmt_news_date(i["date"]), i["text"],
                              i.get("link")) for i in y["items"]]

    autos = {}
    for r in load_releases():
        if r.get("news_skip"):
            continue
        year, md, date_str, text, link, after = _release_news_entry(r)
        autos.setdefault(year, []).append((md, r["cat"], date_str, text,
                                           link, after))
    for lst in autos.values():
        # 日付の新しい順、同日は品番の大きい順に挿入していく
        lst.sort(key=lambda e: (e[0], e[1]), reverse=True)

    out = []
    for year in sorted(set(manual) | set(autos), reverse=True):
        items = list(manual.get(year, []))
        kinds = [None] * len(items)  # None=手動エントリ、(月,日)=自動エントリ
        for md, _cat, date_str, text, link, after in autos.get(year, []):
            pos = len(items)
            for i, (dstr, _t, _l) in enumerate(items):
                if kinds[i] is not None:
                    continue  # 自動同士の順序は挿入順（日付・品番の降順）で保つ
                d = _news_date_tuple(dstr)
                if d is None or d > md:
                    continue
                if d == md and after:
                    continue
                pos = i
                break
            items.insert(pos, (date_str, text, link))
            kinds.insert(pos, md)
        out.append((year, items))
    return out
