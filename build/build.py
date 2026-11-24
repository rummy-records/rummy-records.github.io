#!/usr/bin/env python3
"""サイト全体のビルド入口（フェーズ3〜）。

リポジトリ直下で `python3 build/build.py` を実行すると、
_site/ に以下を生成する：
- 全29ページ（リリース26＋index＋news＋about）
- img/（リポジトリ直下の img/ を複写）
- admin/（Decap CMS。リポジトリ直下の admin/ を複写）
- CNAME（カスタムドメイン）

GitHub Actions（.github/workflows/build.yml）はこのスクリプトを実行し、
_site/ を GitHub Pages にデプロイする。
"""
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SITE = os.path.join(ROOT, "_site")


def main():
    if os.path.exists(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE)
    # build_index が _site/img の一覧を参照するため、先に img を複写する
    shutil.copytree(os.path.join(ROOT, "img"), os.path.join(SITE, "img"))
    shutil.copytree(os.path.join(ROOT, "admin"), os.path.join(SITE, "admin"))
    shutil.copy2(os.path.join(ROOT, "CNAME"), os.path.join(SITE, "CNAME"))
    for mod in ("build_releases", "build_index", "build_news", "build_about"):
        subprocess.run([sys.executable, os.path.join(BASE, mod + ".py")],
                       check=True, cwd=BASE)
    print("build done ->", SITE)


if __name__ == "__main__":
    main()
