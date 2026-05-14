#!/usr/bin/env Rscript

# Render the multilingual website with optional CI site URL injection.
normalize_site_url <- function(url) {
  if (!nzchar(url)) {
    return(url)
  }

  # Avoid double slashes when babelquarto appends language subpaths.
  sub("/+$", "", url)
}

main <- function() {
  if (!requireNamespace("babelquarto", quietly = TRUE)) {
    stop(
      "Package 'babelquarto' is required. Install with ",
      "install.packages('babelquarto', repos = c('https://ropensci.r-universe.dev',",
      " 'https://cloud.r-project.org'))"
    )
  }

  site_url <- Sys.getenv("BABELQUARTO_CI_URL", unset = "")
  site_url <- normalize_site_url(site_url)
  options("babelquarto.quiet" = TRUE)

  if (nzchar(site_url)) {
    message("Rendering with site_url: ", site_url)
    babelquarto::render_website(project_path = ".", site_url = site_url)
  } else {
    message("Rendering without explicit site_url (local preview mode).")
    babelquarto::render_website(project_path = ".")
  }
}

main()
