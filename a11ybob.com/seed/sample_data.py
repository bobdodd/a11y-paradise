"""
Seed the MongoDB database with sample glossary terms and literature reviews.

Usage:
    python seed/sample_data.py

Requires MONGO_URI and MONGO_DB environment variables (or uses defaults).
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "a11y_paradise")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

now = datetime.utcnow().strftime("%Y-%m-%d")

# --- Glossary Terms ---

glossary_terms = [
    {
        "term": "WCAG",
        "aka": ["Web Content Accessibility Guidelines"],
        "definition": "A set of guidelines published by the W3C Web Accessibility Initiative (WAI) that define how to make web content more accessible to people with disabilities. WCAG is organized around four principles: Perceivable, Operable, Understandable, and Robust (POUR). The current version in wide use is WCAG 2.1, with WCAG 2.2 published in 2023.",
        "category": ["standards", "web"],
        "related_terms": ["POUR", "ARIA", "W3C"],
        "sources": ["https://www.w3.org/WAI/standards-guidelines/wcag/"],
        "created": now,
        "updated": now,
    },
    {
        "term": "ARIA",
        "aka": ["Accessible Rich Internet Applications", "WAI-ARIA"],
        "definition": "A W3C specification that provides a framework of roles, states, and properties to make dynamic web content and custom user interface controls accessible to assistive technologies. ARIA supplements HTML semantics where native elements are insufficient. The first rule of ARIA is: if you can use a native HTML element with the semantics and behaviour you require, do so.",
        "category": ["standards", "web"],
        "related_terms": ["WCAG", "screen reader", "role", "semantic HTML"],
        "sources": ["https://www.w3.org/WAI/standards-guidelines/aria/"],
        "created": now,
        "updated": now,
    },
    {
        "term": "Screen reader",
        "aka": [],
        "definition": "An assistive technology application that converts digital text and interface elements into synthesized speech or braille output. Screen readers enable blind and low-vision users to interact with computers, smartphones, and web content. Common screen readers include JAWS, NVDA, VoiceOver (macOS/iOS), and TalkBack (Android).",
        "category": ["assistive technology"],
        "related_terms": ["ARIA", "JAWS", "NVDA", "VoiceOver"],
        "sources": [],
        "created": now,
        "updated": now,
    },
    {
        "term": "POUR",
        "aka": [],
        "definition": "The four foundational principles of WCAG: Perceivable (information must be presentable to users in ways they can perceive), Operable (user interface components must be operable), Understandable (information and operation of the user interface must be understandable), and Robust (content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies).",
        "category": ["standards", "principles"],
        "related_terms": ["WCAG"],
        "sources": ["https://www.w3.org/WAI/WCAG21/Understanding/intro#understanding-the-four-principles-of-accessibility"],
        "created": now,
        "updated": now,
    },
    {
        "term": "PDF/UA",
        "aka": ["ISO 14289", "Universal Accessibility for PDF"],
        "definition": "The international standard (ISO 14289) for accessible PDF documents. PDF/UA defines requirements for PDF content, PDF readers, and assistive technology to ensure accessible interaction with PDF documents. It builds on the existing PDF tag structure and requires proper reading order, alternative text, and logical document structure.",
        "category": ["standards", "documents"],
        "related_terms": ["WCAG", "tagged PDF"],
        "sources": ["https://www.pdfa.org/resource/pdfua-in-a-nutshell/"],
        "created": now,
        "updated": now,
    },
    {
        "term": "Semantic HTML",
        "aka": [],
        "definition": "The practice of using HTML elements according to their intended meaning rather than their visual appearance. Semantic elements like <nav>, <main>, <article>, <aside>, and <header> communicate the structure and purpose of content to browsers, assistive technologies, and search engines. Using semantic HTML is the foundation of web accessibility.",
        "category": ["web", "development"],
        "related_terms": ["ARIA", "landmark"],
        "sources": [],
        "created": now,
        "updated": now,
    },
    {
        "term": "Assistive technology",
        "aka": ["AT"],
        "definition": "Any device, software, or equipment that helps people with disabilities perform tasks that would otherwise be difficult or impossible. In digital accessibility, this includes screen readers, screen magnifiers, switch devices, eye-tracking systems, voice recognition software, and alternative keyboards.",
        "category": ["assistive technology"],
        "related_terms": ["screen reader", "switch access"],
        "sources": [],
        "created": now,
        "updated": now,
    },
    {
        "term": "Alt text",
        "aka": ["Alternative text", "Text alternative"],
        "definition": "A textual description of non-text content (primarily images) that conveys the same information or function as the visual content. Alt text is read by screen readers and displayed when images cannot be loaded. Effective alt text is concise, describes the purpose of the image in context, and avoids phrases like 'image of' or 'picture of'.",
        "category": ["web", "content"],
        "related_terms": ["WCAG", "screen reader"],
        "sources": ["https://www.w3.org/WAI/tutorials/images/"],
        "created": now,
        "updated": now,
    },
]

# --- Literature Reviews ---

literature_reviews = [
    {
        "title": "The WebAIM Million: An Annual Accessibility Analysis of the Top 1,000,000 Home Pages",
        "authors": ["WebAIM"],
        "year": 2024,
        "publication": "WebAIM",
        "doi": "",
        "tags": ["automated testing", "web accessibility", "large-scale analysis"],
        "standards_referenced": ["WCAG 2.1"],
        "summary": "Annual large-scale automated accessibility evaluation of the top one million website home pages. The study consistently reveals widespread accessibility failures, with the majority of pages containing detectable WCAG conformance errors.",
        "key_findings": "96.3% of home pages had detectable WCAG 2 failures. The most common errors were low contrast text, missing alt text for images, empty links, missing form input labels, empty buttons, and missing document language. The average number of errors per page was over 50.",
        "relevance": "Provides essential baseline data on the state of web accessibility. Useful for demonstrating the scale of the problem to stakeholders and for benchmarking organizational progress.",
        "rating": 5,
        "created": now,
        "updated": now,
    },
    {
        "title": "What We Know About Digital Accessibility for People with Cognitive, Learning, and Neurological Disabilities",
        "authors": ["Clayton Lewis"],
        "year": 2023,
        "publication": "ACM Computing Surveys",
        "doi": "",
        "tags": ["cognitive accessibility", "inclusive design", "research review"],
        "standards_referenced": ["WCAG 2.2", "EN 301 549"],
        "summary": "A comprehensive review of research on digital accessibility for people with cognitive, learning, and neurological disabilities. Examines the gap between current standards (which focus primarily on sensory and motor disabilities) and the needs of this broader population.",
        "key_findings": "Current web accessibility standards address only a fraction of the barriers faced by people with cognitive disabilities. The paper identifies key areas where standards fall short and where additional research is needed, including personalization, simplified interfaces, and consistent navigation.",
        "relevance": "Critical reading for anyone working on WCAG conformance who wants to understand the limitations of a purely standards-based approach. Highlights the need for user testing with diverse disability groups.",
        "rating": 4,
        "created": now,
        "updated": now,
    },
    {
        "title": "Born Accessible: Exploring Organizational Practices at CNIB",
        "authors": ["Bob Dodd"],
        "year": 2022,
        "publication": "Research Paper",
        "doi": "",
        "tags": ["organizational practices", "born accessible", "CNIB", "culture"],
        "standards_referenced": ["WCAG 2.1", "EN 301 549", "AODA"],
        "summary": "An exploration of how the Canadian National Institute for the Blind (CNIB) embeds accessibility into its organizational DNA, from procurement and development processes to training and culture. Based on direct experience working within the organization.",
        "key_findings": "Organizations that treat accessibility as a foundational practice rather than a compliance checkbox achieve better outcomes. Key factors include executive buy-in, accessibility expertise embedded in teams, accessible procurement policies, and a culture where accessibility is everyone's responsibility.",
        "relevance": "A practical case study for any organization wanting to move from reactive accessibility remediation to proactive 'born accessible' practices.",
        "rating": 5,
        "created": now,
        "updated": now,
    },
]


def seed():
    # Clear existing data
    db.glossary.drop()
    db.reviews.drop()

    # Insert glossary terms
    result = db.glossary.insert_many(glossary_terms)
    print(f"Inserted {len(result.inserted_ids)} glossary terms.")

    # Insert reviews
    result = db.reviews.insert_many(literature_reviews)
    print(f"Inserted {len(result.inserted_ids)} literature reviews.")

    # Create standard indexes for filtering
    db.glossary.create_index("term")
    db.glossary.create_index("category")
    db.reviews.create_index("tags")
    db.reviews.create_index([("year", -1)])

    print("Database seeded successfully.")
    print()
    print("NOTE: For full-text search, create Atlas Search indexes in the Atlas UI:")
    print("  - Index 'glossary_search' on the 'glossary' collection")
    print("    Fields: term, aka, definition, category (dynamic mapping works too)")
    print("  - Index 'reviews_search' on the 'reviews' collection")
    print("    Fields: title, authors, summary, key_findings, tags, standards_referenced")


if __name__ == "__main__":
    seed()
