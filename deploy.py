"""Build a clean static deployment directory for Cloudflare Pages.

Run this from the repository root:

    python3 deploy.py
"""

import shutil
from pathlib import Path

# Importing build renders the shared header, footer, kit grid, and sample rows
# into the static HTML files before they are copied to the deploy directory.
import build  # noqa: F401


ROOT = Path(__file__).parent
DIST = ROOT / "dist"

if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()

for filename in ("index.html", "styles.css", "kit.js", "robots.txt", "sitemap.xml"):
    shutil.copy2(ROOT / filename, DIST / filename)

for directory in ("assets", "kits"):
    shutil.copytree(ROOT / directory, DIST / directory)

print("built dist/")
