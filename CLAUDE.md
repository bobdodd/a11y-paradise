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

## Adding Glossary Entries via Claude Code

When the user provides an accessibility term to add to the glossary:

1. **Research the term** using web search to write an accurate, comprehensive definition.
2. **Check existing categories** by querying `db.glossary.distinct('category')` to reuse existing values.
3. **Insert directly into MongoDB Atlas** from `a11ybob.com/` using a Python one-liner:

```bash
cd a11ybob.com && source .venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
load_dotenv()
client = MongoClient(os.environ['MONGO_URI'])
db = client[os.environ.get('MONGO_DB', 'a11y_paradise')]
now = datetime.now(timezone.utc).strftime('%Y-%m-%d')
db.glossary.insert_one({
    'term': 'TERM_NAME',
    'aka': ['Alias1'],
    'definition': 'Definition here.',
    'category': ['cat1', 'cat2'],
    'related_terms': ['Existing Term'],
    'sources': ['https://example.com'],
    'created': now,
    'updated': now,
})
print('Done.')
"
```

**Definition style** (see `seed/sample_data.py` for examples):
- 2-4 sentences: what the term means, why it matters for accessibility, practical context
- `related_terms` values must match existing glossary term names exactly
- `sources` should be authoritative (W3C, WAI, MDN, standards bodies)
- `aka` includes common aliases or abbreviations

## Adding Literature Reviews via Claude Code

When the user provides an ACM reference (or similar citation) to add as a review:

1. **Parse the reference** to extract title, authors, year, publication, and DOI.
2. **Fetch the paper's page** (e.g., ACM DL URL via DOI) to get the abstract and understand the paper's scope.
3. **Write the review content** — all three text fields (`summary`, `key_findings`, `relevance`) should be populated. See content guidelines below.
4. **Insert the complete review** into MongoDB.

```bash
cd a11ybob.com && source .venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
load_dotenv()
client = MongoClient(os.environ['MONGO_URI'])
db = client[os.environ.get('MONGO_DB', 'a11y_paradise')]
now = datetime.now(timezone.utc).strftime('%Y-%m-%d')
db.reviews.insert_one({
    'title': 'PAPER_TITLE',
    'authors': ['Author One', 'Author Two'],
    'year': 2024,
    'publication': 'Journal or Conference Name',
    'doi': '10.1145/xxxxxxx.xxxxxxx',
    'tags': [],
    'standards_referenced': [],
    'summary': '',
    'key_findings': '',
    'relevance': '',
    'rating': None,
    'created': now,
    'updated': now,
})
print('Done.')
"
```

**Metadata** — populate from the citation:

- `title`, `authors`, `year`, `publication`, `doi` — extracted directly
- `tags` — infer relevant tags from the paper topic (e.g., `cognitive accessibility`, `screen readers`, `automated testing`)
- `standards_referenced` — any standards mentioned (e.g., `WCAG 2.1`, `EN 301 549`, `ARIA`)
- `rating` — leave as `None` for the user to set

**Review content guidelines** — aim for ~600 words total across the three fields:

- **`summary`** (~250 words): Describe what the paper covers, its methodology, scope, and main arguments. Go beyond the abstract — explain the research context, what problem the authors are addressing, and how they approached it. Write for a practitioner audience, not academics.

- **`key_findings`** (~200 words): The concrete results and conclusions. What did the research discover? Include specific data points, statistics, or outcomes where available. Highlight findings that are actionable or surprising for accessibility practitioners.

- **`relevance`** (~150 words): Why this paper matters for digital accessibility practice. How does it connect to real-world work? What should practitioners, developers, or organizations take away from it? Note any limitations, gaps, or areas where the research could be extended.

**Tone and style:**

- Write as an experienced accessibility professional summarizing for peers
- Be specific and practical — avoid vague academic language
- Connect findings to real-world accessibility work (standards compliance, user testing, organizational practices)
- Use plain language; explain technical concepts where needed

## Deployment

Render auto-deploys from GitHub `main` branch. Config in `render.yaml`. Environment variables (`MONGO_URI`, `MONGO_DB`, `SECRET_KEY`) are set in Render dashboard, not committed.

## Licensing

- Training content (`training/`, `resources/`): **CC BY-SA 4.0**
- Code (`tools/`, Flask app): **GPL v3**
