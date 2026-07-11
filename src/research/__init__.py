"""Facilities research — discover where a company's data centers are, from
public sources (SEC EDGAR filings + first-party location pages).

Standalone from the Streamlit app: run as a CLI, review the CSV/JSON it emits,
then hand-paste vetted rows into ``src.constants`` (HYPERSCALERS /
AI_COMPETITOR_SITES). Nothing here is imported by ``app.py`` — keeping
unverified, scraped data out of the live map until a human signs off.
"""
