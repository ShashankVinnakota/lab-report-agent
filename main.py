import re
import sys
import json
import pdfplumber


def extract_text(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_biomarkers(pdf_path, json_path):
    with open(json_path) as f:
        biomarker_defs = json.load(f)

    lookup = {}
    for b in biomarker_defs:
        canonical = b["biomarker"]
        lookup[canonical.lower()] = canonical
        for alias in b.get("aliases", []):
            lookup[alias.lower()] = canonical

    text = extract_text(pdf_path)
    results = {}

    for line in text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue

        matched_canonical = None
        for alias, canonical in lookup.items():
            if alias in line_stripped.lower():
                matched_canonical = canonical
                break

        if not matched_canonical:
            continue

        if ":" in line_stripped:
            after_colon = line_stripped.split(":", 1)[1]
            numbers = re.findall(r'\b\d+\.?\d*\b', after_colon)
        else:
            numbers = re.findall(r'\b\d+\.?\d*\b', line_stripped)

        if not numbers:
            continue

        value = float(numbers[0])
        if value > 100000:
            continue

        results[matched_canonical] = value

    return results


# ── SET YOUR PATHS HERE ──────────────────────────────────────────
PDF_PATH  = "/Users/shashankvinnakota/Documents/lab report agent/261290000978_Report (1).pdf"
JSON_PATH = "/Users/shashankvinnakota/Documents/lab report agent/medical_benchmark.json"
# ────────────────────────────────────────────────────────────────

result = extract_biomarkers(PDF_PATH, JSON_PATH)
print(result)