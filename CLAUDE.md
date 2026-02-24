# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Start local dev server (Flask on port 8080)
./serve.sh

# Install dependencies
cd a11ybob.com && source .venv/bin/activate && pip install -r requirements.txt

# Seed MongoDB with sample data
cd a11ybob.com && python seed/sample_data.py

# Production start (used by Render)
cd a11ybob.com && gunicorn app:app
```

Port 8080 is used instead of Flask's default 5000 due to macOS AirPlay conflict.

## Architecture

This is a Flask + MongoDB application serving accessibility training content.

**Flask app lives in `a11ybob.com/`:**
- `app.py` — All routes, MongoDB connection, context processors (flat structure, no blueprints)
- `config.py` — Loads `MONGO_URI`, `MONGO_DB`, `SECRET_KEY` from environment via python-dotenv
- `templates/base.html` — Layout template inherited by all pages (skip link, nav with `aria-current`, breadcrumbs)
- `templates/glossary/` and `templates/reviews/` — Feature-specific templates
- `static/css/style.css` — Single stylesheet using CSS custom properties for theming
- `seed/sample_data.py` — Populates MongoDB with 100+ glossary terms and reviews

**Content directories (not part of Flask app):**
- `training/` — Accessibility training content (CC BY-SA 4.0)
- `tools/` — Accessibility tools (GPL v3)
- `resources/` — Curated references

## Database

MongoDB Atlas with two collections:

- **`glossary`** — Fields: term, aka[], definition, category[], related_terms[] (by name, not ID), sources[], created, updated
- **`reviews`** — Fields: title, authors[], year, publication, doi, summary, key_findings, relevance, tags[], standards_referenced[], created, updated

**Atlas Search indexes** (full-text with fuzzy matching, maxEdits: 1):
- `glossary_search` — searches term, aka, definition, category
- `reviews_search` — searches title, authors, summary, key_findings, tags, standards_referenced

## Key Conventions

**Accessibility is paramount** — this is an accessibility training site. All templates must use:
- Semantic HTML (`<main>`, `<nav>`, `<article>`, etc.)
- Labels on all form inputs (use `sr-only` class if visually hidden)
- `aria-live="polite"` on dynamic content regions (search results)
- `aria-current="page"` on active nav links
- `role="search"` on search forms
- Visible focus indicators (3px outline, 2px offset)

**CSS theming** — All colors must use CSS custom properties. Four theme variants must be maintained in `style.css`:
1. Light mode (`:root`)
2. Dark mode (`prefers-color-scheme: dark`)
3. High contrast (`prefers-contrast: more`)
4. Dark + high contrast (combined media query)

**No JavaScript** — The site uses pure semantic HTML/CSS. No JS frameworks or inline scripts (filter forms use `onchange="this.form.submit()"`).

**Templates** extend `base.html` using Jinja2 `{% extends %}` / `{% block %}` pattern.

## Deployment

Render auto-deploys from GitHub `main` branch. Config in `render.yaml`. Environment variables (`MONGO_URI`, `MONGO_DB`, `SECRET_KEY`) are set in Render dashboard, not committed.

## Licensing

- Training content (`training/`, `resources/`): **CC BY-SA 4.0**
- Code (`tools/`, Flask app): **GPL v3**
