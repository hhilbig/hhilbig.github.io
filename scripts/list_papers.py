#!/usr/bin/env python3
"""Extract structured paper data from index.html for status checking.

Default mode prints a JSON list to stdout (one object per <li>).

With ``--check-order``, also verify that the Publications section in
index.html and the Publications section in HHilbig_CV.tex are sorted in
descending year order, with "Forthcoming" entries grouped at the top.
Exits 1 if either file is out of order.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"
CV_TEX = Path(
    "/Users/hanno/Library/CloudStorage/Dropbox/Hanno/03_CV/CV_JobMarket/HHilbig_CV.tex"
)

SECTION_RE = re.compile(
    r'<h2 id="([^"]+)">([^<]+)</h2>\s*<ol[^>]*>(.*?)</ol>',
    re.DOTALL,
)
LI_RE = re.compile(r"<li>(.*?)</li>", re.DOTALL)
TITLE_LINKED_RE = re.compile(
    r'<b>\s*<a\s+href="([^"]+)">\s*(.*?)\s*</a>\s*</b>',
    re.DOTALL,
)
TITLE_UNLINKED_RE = re.compile(r"<b>\s*([^<]+?)\s*</b>", re.DOTALL)
PREPRINT_RE = re.compile(
    r'<i>\s*<a\s+href="([^"]+)">\s*\[Preprint\]\s*</a>\s*</i>',
    re.DOTALL,
)
ABSTRACT_DIV_RE = re.compile(r'<div id="[^"]+"[^>]*>.*?</div>', re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
SPLIT_RE = re.compile(r"<i>\s*<a|<br|<div\b")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", html.unescape(text)).strip()


def extract_li(body: str, section: str):
    title_m = TITLE_LINKED_RE.search(body)
    if title_m:
        primary_url = title_m.group(1)
        title = normalize(title_m.group(2))
        after_idx = title_m.end()
    else:
        title_m = TITLE_UNLINKED_RE.search(body)
        if not title_m:
            return None
        primary_url = None
        title = normalize(title_m.group(1))
        after_idx = title_m.end()

    after = body[after_idx:]
    cleaned = ABSTRACT_DIV_RE.sub("", after)

    preprint_m = PREPRINT_RE.search(cleaned)
    preprint_url = preprint_m.group(1) if preprint_m else None

    cite_html = SPLIT_RE.split(cleaned, maxsplit=1)[0]
    citation = normalize(TAG_RE.sub("", cite_html))

    return {
        "title": title,
        "section": section,
        "primary_url": primary_url,
        "preprint_url": preprint_url,
        "citation": citation,
    }


def extract(html: str):
    out = []
    for m in SECTION_RE.finditer(html):
        section_id = m.group(1)
        section_name = normalize(m.group(2))
        ol_body = m.group(3)
        for li_m in LI_RE.finditer(ol_body):
            paper = extract_li(li_m.group(1), section_name)
            if paper:
                paper["section_id"] = section_id
                out.append(paper)
    return out


# --- Order check ----------------------------------------------------------

YEAR_RE = re.compile(r"\b(20\d{2})\b")
FORTHCOMING_RE = re.compile(r"\bForthcoming\b", re.IGNORECASE)


def sort_key(citation: str):
    """Return (bucket, year) where bucket=1 means Forthcoming, 0 means dated.

    Forthcoming entries get the higher bucket so they appear first in the
    descending order we expect (Forthcoming → most-recent year → ...).
    """
    if FORTHCOMING_RE.search(citation):
        return (1, 9999)
    m = YEAR_RE.search(citation)
    year = int(m.group(1)) if m else 0
    return (0, year)


def check_publication_order_html() -> list[str]:
    """Return list of error messages; empty if order is OK."""
    data = extract(INDEX.read_text(encoding="utf-8"))
    pubs = [p for p in data if p["section_id"] == "publications"]
    return _check_descending(pubs, source="index.html")


def check_publication_order_cv() -> list[str]:
    """Parse HHilbig_CV.tex publications section and verify order."""
    if not CV_TEX.exists():
        return [f"CV not found at {CV_TEX}"]
    text = CV_TEX.read_text(encoding="utf-8")
    m = re.search(
        r"\\section\*\{Publications\}\s*\\begin\{etaremune\}(.*?)\\end\{etaremune\}",
        text,
        re.DOTALL,
    )
    if not m:
        return ["Could not locate \\section*{Publications} block in CV"]
    items = re.findall(r"\\item\s+(.*?)(?=\n\s*\\item|\Z)", m.group(1), re.DOTALL)
    pubs = [{"title": _cv_title(it), "citation": it} for it in items]
    return _check_descending(pubs, source="HHilbig_CV.tex")


def _cv_title(item_body: str) -> str:
    m = re.search(r"\\href\{[^}]*\}\{([^}]*)\}", item_body)
    return normalize(m.group(1)) if m else item_body[:60]


def _check_descending(pubs, source: str) -> list[str]:
    errors = []
    prev_key = None
    prev_title = None
    for p in pubs:
        key = sort_key(p["citation"])
        if prev_key is not None and key > prev_key:
            errors.append(
                f"{source}: '{p['title'][:60]}' (bucket={key}) appears after "
                f"'{prev_title[:60]}' (bucket={prev_key}) — must be descending."
            )
        prev_key = key
        prev_title = p["title"]
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check-order",
        action="store_true",
        help="Verify Publications are sorted descending by year in index.html and CV.",
    )
    args = ap.parse_args()

    if args.check_order:
        errors = check_publication_order_html() + check_publication_order_cv()
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print("Publications order OK in index.html and HHilbig_CV.tex.")
        return 0

    if not INDEX.exists():
        print(f"index.html not found at {INDEX}", file=sys.stderr)
        return 1
    data = extract(INDEX.read_text(encoding="utf-8"))
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
