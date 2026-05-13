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

Each page has an English source file and a Japanese file:

- `index.qmd` and `index.ja.qmd`
- `about.qmd` and `about.ja.qmd`
- `venue.qmd` and `venue.ja.qmd`
- `program.qmd` and `program.ja.qmd`
- `registration.qmd` and `registration.ja.qmd`
- `travel.qmd` and `travel.ja.qmd`
- `contact.qmd` and `contact.ja.qmd`

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

## Add a new page

1. Add `newpage.qmd` and `newpage.ja.qmd`.
2. Add a navbar item in `_quarto.yml`.
3. Commit and push.
