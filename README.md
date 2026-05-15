# International Fern Conference 2027 Website

This repository contains the multilingual Quarto website for the International
Fern Conference 2027.

## Stack

- Quarto website
- babelquarto for multilingual rendering
- GitHub Actions for build and GitHub Pages deployment

## Languages

- Main language: English (`en`)
- Additional language: Japanese (`ja`)

Each page has an English source file and a Japanese file. For example:

- `index.qmd` and `index.ja.qmd`
- `about.qmd` and `about.ja.qmd`

etc.

## Local setup

Install babelquarto in R:

```r
install.packages(
  "babelquarto",
  repos = c("https://ropensci.r-universe.dev", "https://cloud.r-project.org")
)
```

Render locally:

```bash
Rscript scripts/render_site.R
```

Preview the rendered site:

```r
servr::httw("_site")
```

## Deployment notes

This project is configured for a GitHub Pages project site:

- Expected URL shape: `https://USERNAME.github.io/REPOSITORY/`
- Workflow file: `.github/workflows/deploy.yml`

The workflow sets `BABELQUARTO_CI_URL` before rendering so language links work
correctly on subpath-based hosting.

## Content workflow

1. Edit English and Japanese page files directly.
2. Commit and push to `main`.
3. GitHub Actions renders and deploys to GitHub Pages.

## Offline Rendering

Build offline English and Japanese HTML packets plus PDFs from source content.
The script first runs `scripts/render_site.R`, then packages rendered pages from
`_site` into offline HTML, and finally prints PDFs with Playwright.
No AI/content-generation step is used in this pipeline.

Output files are written to `local/` by default:

```bash
python3 scripts/build_offline_packet.py
```

Create only the offline HTML files and skip PDF rendering:

```bash
python3 scripts/build_offline_packet.py --html-only
```

Write output files to a custom directory:

```bash
python3 scripts/build_offline_packet.py --output-dir path/to/output
```

If `_site` is already up to date and you want to skip re-rendering:

```bash
python3 scripts/build_offline_packet.py --skip-render
```

If Playwright is not installed, install it once:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

## Add a new page

1. Add `newpage.qmd` and `newpage.ja.qmd`.
2. Add a navbar items in `_quarto-en.yml` and `_quarto-ja.yml`.
3. Commit and push.
