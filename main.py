
import re
import sys
import pdfplumber


# Only lines containing these words are considered biomarker results
VALID_UNITS = {"mg/L", "g/dL", "g/L", "mg/dL", "mmol/L", "umol/L", "nmol/L",
               "IU/L", "U/L", "mIU/L", "uIU/mL", "ng/mL", "pg/mL", "ng/dL",
               "ug/dL", "ug/L", "mmHg", "%", "fL", "pg", "10^3/uL", "10^6/uL",
               "cells/uL", "mm/hr", "sec", "ratio", "mEq/L", "mosm/kg"}

# Lines containing these are definitely NOT biomarker results
SKIP_KEYWORDS = ["name", "age", "gender", "ref.", "ref by", "sample type",
                 "registered", "collected", "released", "printed", "regn",
                 "registration", "method", "interpretation", "comment",
                 "according", "low", "average", "high", "cardio", "risk",
                 "level", "increased", "reveals", "persistent", "dr.", "dr ",
                 "test name", "result", "biological", "reference interval"]


def extract_biomarkers(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    biomarkers = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Skip lines with known non-biomarker keywords
        if any(kw in line.lower() for kw in SKIP_KEYWORDS):
            continue

        # Match: "Test Name : 0.82 mg/L"
        match = re.search(r'^(.+?)\s*:\s*(\d+\.?\d*)\s+([^\s<>]+)', line)
        if not match:
            continue

        name = match.group(1).strip()
        value = float(match.group(2))
        unit = match.group(3).strip()

        # Only accept if unit looks medical (not a date, ID, etc.)
        if not any(u.lower() in unit.lower() for u in VALID_UNITS):
            continue

        biomarkers[name] = {"value": value, "unit": unit}

    return biomarkers


if __name__ == "__main__":
    path = "/Users/shashankvinnakota/Documents/lab report agent/261290000978_Report (1).pdf"
    result = extract_biomarkers(path)
    for name, data in result.items():
        print(f"{name}: {data['value']} {data['unit']}")
    print("\nAs dict:", result)
