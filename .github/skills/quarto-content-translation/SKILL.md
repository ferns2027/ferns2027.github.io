---
name: quarto-content-translation
description: >-
  Translate Quarto content from the main language to target languages in
  _quarto.yml. Use for bilingual or multilingual updates, content-only
  translation, and git-incremental translation of changed content.
argument-hint: >-
  mode=full|git-incremental, base-ref=<git ref>, files=<optional list>
---

# Quarto Content Translation

Translate Quarto page content from the main language into the target languages
configured in `_quarto.yml`, while preserving Markdown and code exactly.

## What This Skill Produces

- Updated translated `.qmd` files for each target language.
- A translation summary listing files processed and skipped.
- In `git-incremental` mode, translations only for content changed since a
  baseline ref.

## When to Use

Use this skill when you need to:

- Keep multilingual Quarto pages synchronized with main-language updates.
- Translate only text content while preserving all formatting and code blocks.
- Generate translation updates only for changed sections using git history.

## Inputs

Optional arguments:

- `mode`: `full` or `git-incremental`.
- `base-ref`: Commit, tag, or branch for incremental comparison.
- `files`: Optional source-language `.qmd` files to limit scope.
- `session-tag`: Optional marker used to identify the last translation session.

Defaults:

- `mode=full` if not specified.
- In `git-incremental` mode, prefer `base-ref` if provided.
- If `base-ref` is missing, automatically detect the latest commit that
  touched any target language `.ja.qmd` file and use that as the baseline.
- Update whole sections (all content under a heading) if any change occurs in
  that section.
- Translate changed human-readable frontmatter values.

## Translation Rules (Content Only)

Translate human-language content, but keep technical structure unchanged.

Do translate:

- YAML frontmatter values that are human-readable text.
- Headings, paragraph text, list item text, blockquote text.
- Table cell prose, figure captions, and callout prose.

Do not modify:

- YAML keys.
- Markdown structure (`#`, `-`, numbering, table pipes, callout syntax).
- Code fences and code fence info strings.
- Inline code, code blocks, math, citations, cross-reference IDs, and URLs.
- Filename conventions or language suffixes.

## File and Language Discovery

1. Read `_quarto.yml`.
2. Resolve main language from `babelquarto.mainlanguage`.
3. Resolve target languages from `babelquarto.languages`.
4. Build source file list:
   - If `files` is provided, use only those files.
   - Otherwise use main-language `.qmd` files without language suffixes.
5. For each source file (for example `index.qmd`), map target files as
   `index.<lang>.qmd`.

## Mode A: Full Translation

1. Translate all discovered source files.
2. Create missing target files if needed.
3. Preserve all non-content syntax exactly.
4. Return a summary of files translated.

## Mode B: Git-Incremental Translation

1. Determine baseline:
   - If `base-ref` is provided, use it.
   - Else, use the latest commit that touched any target language files.
2. Compute changed source files using git diff from baseline to `HEAD`.
3. For each changed source file, identify modified heading sections.
4. Update target language files by translating all content under each
   changed section heading.
5. Keep frontmatter translated if any frontmatter values changed.
6. Report:
   - baseline used
   - files changed
   - sections updated
   - files skipped

## Section Matching for Incremental Updates

In incremental mode, match and update whole sections (all content under a
heading) if any content in that section changed:

- Identify changed lines in source files using git diff.
- For each changed line, find its enclosing heading.
- Translate all content under that heading in the target language file.
- This ensures consistency and avoids orphaned or partially-translated content.

If a heading structure changed (reordered, deleted, added), flag for manual
review of the affected target file.


## Quality Checks

Before finishing, confirm all checks pass:

1. All translated files keep valid `.qmd` structure.
2. Markdown syntax, code, links, and math are unchanged except translated prose.
3. Target language filenames follow babelquarto suffix conventions.
4. In incremental mode, unchanged segments are untouched.
5. A concise change summary is provided.

## Failure and Fallback Behavior

- If `_quarto.yml` has no `babelquarto` language config, stop and ask for
  language settings.
- If the auto-detected baseline is empty (no prior target-file commits), ask
  whether to use the earliest commit or fall back to full translation mode.
- If section heading structure is ambiguous or has changed significantly,
  flag the file for manual review rather than guessing.

## Suggested Prompt Patterns

- "Translate all English pages to configured target languages."
- "Run git-incremental translation from base-ref=<commit>."
- "Translate only index.qmd and about.qmd to all target languages."
