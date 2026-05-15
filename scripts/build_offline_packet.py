#!/usr/bin/env python3
"""Build offline EN/JA HTML packets and PDFs from rendered Quarto pages.

This script reads rendered pages in `_site/` and `_site/ja/`, extracts the
main content for each page, builds two standalone offline HTML files, and
optionally renders PDFs with Playwright/Chromium.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

PAGES_EN = [
    ("index", "Home"),
    ("about", "About"),
    ("venue", "Venue"),
    ("program", "Program"),
    ("registration", "Registration"),
    ("travel", "Travel"),
    ("contact", "Contact"),
]

PAGES_JA = [
    ("index", "ホーム"),
    ("about", "概要"),
    ("venue", "会場案内"),
    ("program", "プログラム"),
    ("registration", "参加登録"),
    ("travel", "交通案内"),
    ("contact", "お問い合わせ"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build offline EN/JA HTML files from _site and optionally render "
            "PDFs with Playwright."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root containing _site/ (default: current directory)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Only create offline HTML files; skip PDF generation.",
    )
    parser.add_argument(
      "--skip-render",
      action="store_true",
      help=(
        "Skip running `Rscript scripts/render_site.R` before building "
        "offline assets."
      ),
    )
    parser.add_argument(
      "--output-dir",
      type=Path,
      default=Path("local"),
      help=(
        "Directory (relative to project root unless absolute) for offline "
        "HTML/PDF outputs (default: local)"
      ),
    )
    return parser.parse_args()


def must_exist(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        msg = "Missing required files/directories:\n- " + "\n- ".join(missing)
        raise FileNotFoundError(msg)


def extract_main(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<main class="content"[^>]*>(.*?)</main><!-- /main -->',
        text,
        flags=re.S,
    )
    if not match:
        raise RuntimeError(f"Could not extract <main> from {path}")

    # Keep rendered page content verbatim to avoid any content drift.
    return match.group(1).strip()


def render_site(project_root: Path) -> None:
    script_path = project_root / "scripts" / "render_site.R"
    must_exist([script_path])
    subprocess.run(
        ["Rscript", str(script_path)],
        cwd=project_root,
        check=True,
    )


def build_html(
    *,
    lang: str,
    site_dir: Path,
    pages: list[tuple[str, str]],
    site_title: str,
    doc_title: str,
    font_stack: str,
) -> str:
    sections = []
    toc_items = []

    for slug, label in pages:
        html = extract_main(site_dir / f"{slug}.html")
        section_id = f"section-{slug}"
        toc_items.append(f'<li><a href="#{section_id}">{label}</a></li>')
        sections.append(
            f'<section id="{section_id}" class="page-section">\n'
            f'  <h2 class="page-label">{label}</h2>\n'
            f"{html}\n"
            f"</section>"
        )

    return f"""<!DOCTYPE html>
<html lang=\"{lang}\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{doc_title}</title>
  <style>
    :root {{
      --fern-accent: #3fb618;
      --fern-accent-hover: #339214;
      --fern-deep: #1f5b3a;
      --fern-mid: #2f7b50;
      --mist: #eef5ef;
      --ink: #1f2933;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: {font_stack};
      line-height: 1.6;
      color: var(--ink);
      background: radial-gradient(circle at 10% 10%, #f5faf6, #ffffff 40%),
                  linear-gradient(180deg, #ffffff 0%, var(--mist) 100%);
    }}

    .wrap {{
      max-width: 960px;
      margin: 0 auto;
      padding: 24px;
    }}

    .masthead {{
      margin-bottom: 24px;
      border-bottom: 3px solid var(--fern-mid);
      padding-bottom: 12px;
    }}

    .site-title {{
      margin: 0;
      color: var(--fern-deep);
      font-size: 2rem;
    }}

    .toc ul {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 16px;
      list-style: none;
      margin: 12px 0 0;
      padding: 0;
    }}

    .toc a {{
      color: var(--fern-mid);
      text-decoration: none;
      font-weight: 600;
    }}

    .toc a:hover,
    .toc a:focus {{
      color: var(--fern-accent-hover);
      text-decoration: underline;
    }}

    .page-section {{
      margin: 28px 0 42px;
      padding-bottom: 20px;
      border-bottom: 1px solid #d7e5da;
      page-break-inside: avoid;
    }}

    .page-label {{
      margin: 0 0 12px;
      color: var(--fern-deep);
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .page-section h1,
    .page-section h2,
    .page-section h3,
    .page-section h4 {{
      color: var(--fern-deep);
    }}

    .page-section a {{
      color: var(--fern-mid);
      text-decoration: none;
    }}

    .page-section a:hover,
    .page-section a:focus {{
      color: var(--fern-accent-hover);
      text-decoration: underline;
    }}

    @media print {{
      body {{ background: #fff; }}
      .wrap {{ max-width: none; padding: 0.5in; }}
      .toc {{ page-break-after: always; }}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <header class=\"masthead\">
      <h1 class=\"site-title\">{site_title}</h1>
      <nav class=\"toc\" aria-label=\"Table of contents\">
        <ul>
          {''.join(toc_items)}
        </ul>
      </nav>
    </header>
    {''.join(sections)}
  </div>
</body>
</html>
"""


async def render_pdfs(output_dir: Path) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed. Install with: python3 -m pip install "
            "playwright && python3 -m playwright install chromium"
        ) from exc

    jobs = [
        ("Ferns2027_Website_Offline.html", "Ferns2027_Conference_EN.pdf"),
        ("Ferns2027_Website_JA_Offline.html", "Ferns2027_Conference_JA.pdf"),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for html_name, pdf_name in jobs:
            page = await browser.new_page()
            file_url = (output_dir / html_name).resolve().as_uri()
            await page.goto(file_url, wait_until="networkidle")
            await page.pdf(
                path=str(output_dir / pdf_name),
                format="A4",
                print_background=True,
                margin={
                    "top": "12mm",
                    "right": "12mm",
                    "bottom": "12mm",
                    "left": "12mm",
                },
            )
            await page.close()
        await browser.close()


def build_offline_assets(project_root: Path, output_dir: Path) -> None:
    site_dir = project_root / "_site"
    site_ja_dir = site_dir / "ja"

    must_exist(
        [
            site_dir,
            site_ja_dir,
            *(site_dir / f"{slug}.html" for slug, _ in PAGES_EN),
            *(site_ja_dir / f"{slug}.html" for slug, _ in PAGES_JA),
        ]
    )

    en_html = build_html(
        lang="en",
        site_dir=site_dir,
        pages=PAGES_EN,
        site_title="Ferns 2027 Offline Packet (English)",
        doc_title="Ferns 2027 Offline Packet (English)",
        font_stack=(
            '"Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", '
            'Roboto, "Helvetica Neue", Arial, sans-serif'
        ),
    )

    ja_html = build_html(
        lang="ja",
        site_dir=site_ja_dir,
        pages=PAGES_JA,
        site_title="国際シダ会議 2027 オフライン資料（日本語）",
        doc_title="国際シダ会議 2027 オフライン資料（日本語）",
        font_stack='"Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif',
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "Ferns2027_Website_Offline.html").write_text(
        en_html,
        encoding="utf-8",
    )
    (output_dir / "Ferns2027_Website_JA_Offline.html").write_text(
        ja_html,
        encoding="utf-8",
    )


def resolve_output_dir(project_root: Path, output_dir: Path) -> Path:
    if output_dir.is_absolute():
        return output_dir
    return project_root / output_dir


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = resolve_output_dir(project_root, args.output_dir)

    try:
        if not args.skip_render:
            print("Rendering site from source with scripts/render_site.R...")
            render_site(project_root)
        else:
            print("Skipping render step (--skip-render).")

        build_offline_assets(project_root, output_dir)
        print(f"Built offline HTML files in {output_dir}:")
        print("- Ferns2027_Website_Offline.html")
        print("- Ferns2027_Website_JA_Offline.html")

        if not args.html_only:
            asyncio.run(render_pdfs(output_dir))
            print(f"Built offline PDFs in {output_dir}:")
            print("- Ferns2027_Conference_EN.pdf")
            print("- Ferns2027_Conference_JA.pdf")
        else:
            print("Skipped PDF generation (--html-only).")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
