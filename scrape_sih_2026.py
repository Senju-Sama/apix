"""
Smart India Hackathon (SIH 2026) Problem Statements Scraper & Exporter
Fetches all problem statements from https://sih.gov.in/sih2026PS and saves them into CSV and JSON formats.
"""

import os
import sys
import ssl
import csv
import json
import re
import urllib.request
from bs4 import BeautifulSoup

URL = "https://sih.gov.in/sih2026PS"
CSV_FILENAME = "sih_2026_problem_statements.csv"
JSON_FILENAME = "sih_2026_problem_statements.json"

HEADERS = [
    "S.No.",
    "PS Number",
    "Problem Statement ID",
    "Title",
    "Category",
    "Theme",
    "Organization",
    "Department",
    "Submitted Ideas Count",
    "Deadline",
    "Full Description",
    "YouTube Link",
    "Dataset Link",
    "Contact Info"
]

def clean_text(text: str) -> str:
    """Clean and normalize whitespace while preserving meaningful text."""
    if not text:
        return ""
    # Replace non-breaking spaces and excessive whitespace
    text = text.replace("\xa0", " ")
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3 or more newlines with 2 newlines
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()

def fetch_page_content(url: str) -> str:
    """Download HTML content from the SIH portal."""
    print(f"[+] Fetching problem statements from: {url}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def parse_problem_statements(html: str):
    """Parse table rows and modal dialogs from the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "dataTablePS"})
    if not table:
        raise ValueError("Could not locate table with id='dataTablePS' on the page.")

    tbody = table.find("tbody")
    if not tbody:
        raise ValueError("Could not locate tbody inside dataTablePS.")

    rows = tbody.find_all("tr", recursive=False)
    print(f"[+] Found {len(rows)} problem statement rows in the table.")

    records = []
    for idx, row in enumerate(rows, start=1):
        tds = row.find_all("td", recursive=False)
        if len(tds) < 8:
            continue

        s_no = clean_text(tds[0].get_text())
        org_main = clean_text(tds[1].get_text())
        category_main = clean_text(tds[3].get_text())
        ps_number = clean_text(tds[4].get_text())
        submitted_count = clean_text(tds[5].get_text())
        theme_main = clean_text(tds[6].get_text())
        deadline = clean_text(tds[7].get_text())

        # Inspect embedded modal for full details
        modal = row.find("div", class_=lambda c: c and "modal" in c)
        modal_dict = {}

        if modal:
            modal_table = modal.find("table")
            if modal_table:
                for m_tr in modal_table.find_all("tr"):
                    cells = m_tr.find_all(["th", "td"])
                    if len(cells) >= 2:
                        label = clean_text(cells[0].get_text())
                        # Check for hyperlink inside cell
                        a_tag = cells[1].find("a")
                        val = clean_text(cells[1].get_text())
                        if a_tag and a_tag.get("href"):
                            href = a_tag["href"].strip()
                            if href and href not in val and not href.startswith("javascript"):
                                val = f"{val} ({href})" if val else href
                        modal_dict[label] = val

        # Fallback to anchor title if title missing from modal
        title = modal_dict.get("Problem Statement Title", "")
        if not title:
            title_anchor = tds[2].find("a")
            title = clean_text(title_anchor.get_text()) if title_anchor else clean_text(tds[2].get_text())

        record = {
            "S.No.": s_no or str(idx),
            "PS Number": ps_number,
            "Problem Statement ID": modal_dict.get("Problem Statement ID", ps_number.replace("SIH", "")),
            "Title": title,
            "Category": modal_dict.get("Category", category_main),
            "Theme": modal_dict.get("Theme", theme_main),
            "Organization": modal_dict.get("Organization", org_main),
            "Department": modal_dict.get("Department", ""),
            "Submitted Ideas Count": submitted_count,
            "Deadline": deadline,
            "Full Description": modal_dict.get("Description", ""),
            "YouTube Link": modal_dict.get("Youtube Link", ""),
            "Dataset Link": modal_dict.get("Dataset Link", ""),
            "Contact Info": modal_dict.get("Contact info", "")
        }
        records.append(record)

    return records

def export_to_csv(records, output_path: str):
    """Write records to CSV with utf-8-sig encoding for Excel compatibility."""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    print(f"[OK] Successfully exported {len(records)} records to CSV: {output_path}")

def export_to_json(records, output_path: str):
    """Write records to formatted JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"[OK] Successfully exported {len(records)} records to JSON: {output_path}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, CSV_FILENAME)
    json_path = os.path.join(base_dir, JSON_FILENAME)

    try:
        html = fetch_page_content(URL)
        records = parse_problem_statements(html)

        if not records:
            print("[!] Warning: No records were extracted. Check page layout.")
            sys.exit(1)

        export_to_csv(records, csv_path)
        export_to_json(records, json_path)

        # Summary statistics
        categories = {}
        themes = {}
        for r in records:
            cat = r["Category"] or "Unknown"
            thm = r["Theme"] or "Unknown"
            categories[cat] = categories.get(cat, 0) + 1
            themes[thm] = themes.get(thm, 0) + 1

        print("\n" + "="*50)
        print("EXTRACTION SUMMARY:")
        print(f"Total Problem Statements Extracted: {len(records)}")
        print("\nBy Category:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count}")
        print("\nTop Themes:")
        for thm, count in sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {thm}: {count}")
        print("="*50)

    except Exception as e:
        print(f"[ERROR] Error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
