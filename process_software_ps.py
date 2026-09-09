"""
SIH 2026 Software Problem Statements Cleaner, Analyzer & Ranker
Filters 178 Software statements, cleans text/symbols, evaluates:
1. Difficulty Score (1-10)
2. AI Assistance Score (1-10)
3. Our Team Fit Score (1-10) & Role Roadmap
Exports to Excel-ready CSV (utf-8-sig) and JSON.
"""

import os
import sys
import csv
import json
import re

INPUT_CSV = "sih_2026_problem_statements.csv"
OUTPUT_CSV = "sih_2026_software_problem_statements_ranked.csv"
OUTPUT_JSON = "sih_2026_software_problem_statements_ranked.json"

OUTPUT_HEADERS = [
    "Our Team Fit Rank",
    "Our Team Fit Score (1-10)",
    "Our Team Fit Level",
    "Our Team Role & Strategy",
    "Difficulty Score (1-10)",
    "Difficulty Level",
    "Difficulty Rationale",
    "AI Assistance Score (1-10)",
    "AI Assistance Level",
    "AI Assistance Rationale",
    "PS Number",
    "Problem Statement ID",
    "Title",
    "Theme",
    "Organization",
    "Department",
    "Key Tech Stack / Recommended Skills",
    "Hackathon Feasibility",
    "Submitted Ideas Count",
    "Competition Level",
    "Cleaned Background",
    "Cleaned Core Problem",
    "Cleaned Expected Solution",
    "Full Cleaned Description",
    "Deadline",
    "External Links"
]

def clean_text(text: str) -> str:
    """Normalize whitespace, convert corrupt bullets/quotes, and clean symbols."""
    if not text:
        return ""
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")
    # Replace smart quotes with standard quotes
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    # Replace em-dashes and en-dashes
    text = text.replace("\u2014", " - ").replace("\u2013", " - ")
    # Convert bullets to markdown dashes
    text = text.replace("\u2022", "\n- ")
    text = text.replace("\u25cf", "\n- ")
    text = text.replace("\u25aa", "\n- ")
    # Clean up multiple spaces and excessive newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()

def parse_sections(desc: str):
    """Decompose description into Background, Core Problem, and Expected Solution."""
    cleaned = clean_text(desc)
    bg, prob, sol = "", "", ""

    # Search for section markers
    bg_match = re.search(r"(?:Background\s*:?)(.*?)(?=(?:Description\s*:?|Problem\s*Description\s*:?|Objective\s*:?|Expected\s*Solution\s*:?)|$)", cleaned, re.IGNORECASE | re.DOTALL)
    if bg_match:
        bg = bg_match.group(1).strip()

    prob_match = re.search(r"(?:Description\s*:?|Problem\s*Description\s*:?|Problem\s*Statement\s*:?)(.*?)(?=(?:Expected\s*Solution\s*:?|Key\s*Deliverables\s*:?|Outcomes\s*:?)|$)", cleaned, re.IGNORECASE | re.DOTALL)
    if prob_match:
        prob = prob_match.group(1).strip()
    elif not bg:
        prob = cleaned

    sol_match = re.search(r"(?:Expected\s*Solution\s*:?|Key\s*Deliverables\s*:?|Solution\s*:?)(.*)", cleaned, re.IGNORECASE | re.DOTALL)
    if sol_match:
        sol = sol_match.group(1).strip()

    # Fallbacks if regex didn't isolate
    if not bg and not prob and not sol:
        prob = cleaned

    return clean_text(bg), clean_text(prob), clean_text(sol), cleaned

def parse_submission_count(count_str: str):
    """Parse '9/500' into integer and competition level."""
    if not count_str:
        return 0, "Low (0-5 ideas)"
    match = re.search(r"(\d+)", count_str)
    count = int(match.group(1)) if match else 0
    if count <= 5:
        level = "Low (0-5 ideas)"
    elif count <= 20:
        level = "Medium (6-20 ideas)"
    else:
        level = "High (>20 ideas)"
    return count, level

def analyze_statement(record: dict):
    """
    Perform multi-dimensional analysis on a software problem statement:
    - Difficulty Score (1-10)
    - AI Assistance Score (1-10)
    - Our Team Fit Score (1-10)
    """
    title = record.get("Title", "")
    theme = record.get("Theme", "")
    org = record.get("Organization", "")
    desc = record.get("Full Description", "")
    combined_text = f"{title} {theme} {org} {desc}".lower()

    # -------------------------------------------------------------
    # 1. DIFFICULTY SCORING (1.0 to 10.0)
    # -------------------------------------------------------------
    # Baseline difficulty based on domain
    diff_score = 4.5

    # Algorithmic & AI/ML Complexity
    if any(k in combined_text for k in ["electronic warfare", "rf scan", "interlocking", "railway signalling", "mine subsidence", "short-circuit test", "iec 60898", "cadastral", "3d ulpin", "manganese reserve"]):
        diff_score += 3.2
    elif any(k in combined_text for k in ["anpr", "multi-camera", "satellite", "sar", "drone imagery", "hyperspectral", "blockchain", "smart contract", "biometric", "point cloud"]):
        diff_score += 2.2
    elif any(k in combined_text for k in ["predictive analytics", "machine learning", "deep learning", "yolo", "computer vision", "ocr", "nlp", "llm", "gis", "geospatial"]):
        diff_score += 1.2
    elif any(k in combined_text for k in ["dashboard", "portal", "management system", "tracking system", "complaint", "advisory", "booking", "inventory"]):
        diff_score -= 0.5

    # Data / Sensor Dependencies
    if any(k in combined_text for k in ["sensor data", "hardware", "iot device", "low visibility", "underground coal", "borehole", "radar", "iec standard"]):
        diff_score += 1.2
    elif any(k in combined_text for k in ["satellite feeds", "imd weather", "drone", "real-time telemetry"]):
        diff_score += 0.8
    elif any(k in combined_text for k in ["web scraping", "open data", "public api", "image upload", "form"]):
        diff_score -= 0.4

    # Bound difficulty between 1.5 and 9.8
    diff_score = max(1.5, min(9.8, round(diff_score, 1)))

    if diff_score < 3.5:
        diff_level = "Very Low"
    elif diff_score < 5.5:
        diff_level = "Low"
    elif diff_score < 7.5:
        diff_level = "Medium"
    elif diff_score < 8.8:
        diff_level = "High"
    else:
        diff_level = "Very High"

    # Difficulty Rationale
    diff_reasons = []
    if diff_score >= 8.5:
        diff_reasons.append("Requires deep safety-critical or specialized physics/hardware domain knowledge (e.g. railway signalling, RF scan, or IEC standards).")
        diff_reasons.append("Complex algorithmic optimization or restricted proprietary data environments.")
    elif diff_score >= 7.0:
        diff_reasons.append("Demands multi-stage pipelines: real-time computer vision, spatial geometry/GIS calculations, or blockchain consensus.")
        diff_reasons.append("Integration across heterogeneous data streams (satellite, camera feeds, or drone spatial layers).")
    elif diff_score >= 5.0:
        diff_reasons.append("Standard multi-tier platform requiring user authentication, predictive ML/NLP models, and external API connectors.")
        diff_reasons.append("Needs robust state management and automated notification workflows.")
    else:
        diff_reasons.append("Primarily CRUD database management, user verification workflows, and standard responsive web/mobile interfaces.")
        diff_reasons.append("Standard APIs and existing open-source libraries can satisfy core requirements.")
    diff_rationale = " ".join(diff_reasons)

    # -------------------------------------------------------------
    # 2. AI ASSISTANCE SCORING (1.0 to 10.0)
    # (10 = 100% prompt-to-app zero-code, 1 = manual engineering grind)
    # -------------------------------------------------------------
    ai_score = 6.5

    # High AI boost: standard web apps, CRUD, standard dashboards, LLM RAG, scrapers, recommendation engines
    if any(k in combined_text for k in ["portal", "dashboard", "advisory", "chatbot", "recommendation", "directory", "monitoring platform", "compliance check", "matching"]):
        ai_score += 1.8
    if any(k in combined_text for k in ["web scraping", "api", "analytics", "reporting solution", "management system", "verification"]):
        ai_score += 1.0

    # Low AI penalty: specialized physics, defense, electrical test rigs, railway interlocking, custom hardware
    if any(k in combined_text for k in ["electronic warfare", "rf scan", "iec 60898", "is 10810", "interlocking", "underground coal", "short-circuit"]):
        ai_score -= 4.5
    elif any(k in combined_text for k in ["cadastral", "3d ulpin", "mine subsidence", "drone imagery", "anpr trajectory", "blockchain"]):
        ai_score -= 1.8
    elif any(k in combined_text for k in ["satellite", "gis-based", "sensor data"]):
        ai_score -= 0.8

    ai_score = max(1.2, min(9.7, round(ai_score, 1)))

    if ai_score >= 8.5:
        ai_level = "Pure AI / Zero-Code (85-100%)"
        ai_rationale = "Modern AI coding tools (Claude, Cursor, Bolt, v0) can generate virtually 90-100% of the working full-stack code, UI components, database schema, and mock APIs directly from plain-English prompts with zero manual coding."
    elif ai_score >= 7.0:
        ai_level = "High AI Assistance (70-84%)"
        ai_rationale = "AI can generate the complete frontend, REST APIs, and integrate standard pre-trained models (YOLO/HuggingFace/OpenAI). Human only needs to configure API keys, test UI flow, and resolve environment setup."
    elif ai_score >= 5.0:
        ai_level = "Moderate AI Assistance (50-69%)"
        ai_rationale = "AI can scaffold architecture, database schema, and UI pages, but human guidance is needed to debug spatial/GIS queries, pipeline integrations, or custom ML model training."
    elif ai_score >= 3.0:
        ai_level = "Low AI Assistance (30-49%)"
        ai_rationale = "Requires domain-specific algorithms or complex spatial topology where AI frequently hallucinates equations or edge cases. Requires significant human manual debugging and architectural tuning."
    else:
        ai_level = "Heavy Human Grind / Minimal AI (10-29%)"
        ai_rationale = "Safety-critical, proprietary hardware protocols or defense domain. Zero-knowledge builders cannot build this with AI alone; deep domain engineering and manual coding required."

    # -------------------------------------------------------------
    # 3. OUR TEAM FIT SCORING (1.0 to 10.0)
    # Matching:
    # - Lead: Web scraping, AI-assisted full-stack, animations, APIs, pre-trained ML/DL, deployment
    # - Sukesh: React frontend & backend architecture, robust web dev
    # - Shivam: Deep UI/UX design, visual polish, flow optimization
    # - Yash: Sharp strategic thinking, coordination, pitch flow & presentation
    # - 2 Open Slots: To fill problem-specific requirements
    # -------------------------------------------------------------
    team_score = 6.0

    # Boost for Web Scraping / Data Aggregation / Public Web Data
    if any(k in combined_text for k in ["scrape", "crawling", "aggregat", "market prices", "portal", "reporting solution", "multi-source", "intelligence platform", "harmonization"]):
        team_score += 1.8

    # Boost for High-Impact UI/UX & Animations (Shivam's & Lead's playground)
    if any(k in combined_text for k in ["dashboard", "interactive", "gamification", "elderly", "citizen", "mobile app", "visualization", "heatmaps", "platform"]):
        team_score += 1.2

    # Boost for React / Full-Stack & APIs (Sukesh & Lead)
    if any(k in combined_text for k in ["platform", "web application", "cloud-based", "portal", "management system", "advisory", "smart governance"]):
        team_score += 1.0

    # Boost for Pre-trained ML / LLM APIs / Computer Vision
    if any(k in combined_text for k in ["ai-based", "ai-powered", "ai-driven", "llm", "nlp", "chatbot", "early warning", "recommendation"]):
        team_score += 0.8

    # Penalties for things our team doesn't specialize in (hardware rigs, RF warfare, safety interlocking)
    if any(k in combined_text for k in ["electronic warfare", "iec 60898", "short-circuit test", "cable specimen", "is 10810"]):
        team_score -= 4.0
    elif any(k in combined_text for k in ["interlocking", "underground coal mine", "manganese reserve"]):
        team_score -= 2.2
    elif any(k in combined_text for k in ["3d ulpin", "cadastral feature", "point cloud"]):
        team_score -= 1.0

    # Bonus if high AI assistance makes it super fast for our AI-accelerated workflow
    if ai_score >= 8.0:
        team_score += 0.7

    team_score = max(1.5, min(9.9, round(team_score, 1)))

    if team_score >= 8.8:
        team_level = "Jackpot Match (8.8 - 10.0)"
    elif team_score >= 7.5:
        team_level = "Strong Match (7.5 - 8.7)"
    elif team_score >= 5.5:
        team_level = "Viable with Effort (5.5 - 7.4)"
    else:
        team_level = "Avoid / Low Fit (< 5.5)"

    # Team Strategy & Role Breakdown
    if team_score >= 8.0:
        strategy = (
            "PERFECT FIT. "
            "Lead (You): Build web scrapers / data feeds, integrate pre-trained AI/LLM APIs, code dynamic UI animations, handle cloud deployment. "
            "Sukesh: Architect robust React frontend, state management, and backend REST/GraphQL APIs. "
            "Shivam: Design high-polish, award-winning Figma UI/UX, user flows, and micro-interactions. "
            "Yash: Coordinate milestones, structure user personas, build high-impact presentation PPT & live demo script. "
            "2 Open Slots: Recruit 1 Mobile/App dev (Flutter/React Native) or 1 Python Data/Testing generalist."
        )
    elif team_score >= 6.5:
        strategy = (
            "SOLID MATCH. "
            "Lead (You): Lead AI-assisted pipeline, pre-trained model setup (YOLO/NLP/RAG), API connectors. "
            "Sukesh: Build core React web application, database models, and authentication. "
            "Shivam: Deeply polish the dashboard UI, data visualization layouts, and accessibility. "
            "Yash: Manage team schedule, validate government requirements, structure pitch deck. "
            "2 Open Slots: Recruit 1 ML/Data engineer (for dataset prep) and 1 pitch presenter / domain researcher."
        )
    elif team_score >= 5.0:
        strategy = (
            "MODERATE FIT (Requires Specific Skills). "
            "Lead & Sukesh: Collaborate heavily on data engineering and complex backend logic with AI assistance. "
            "Shivam: Design intuitive UI to simplify complex domain workflows for judges. "
            "Yash: Coordinate problem-specific research and judge alignment. "
            "2 Open Slots: MUST recruit 1 specialist with GIS/Spatial or Data Science background to bridge technical gap."
        )
    else:
        strategy = (
            "NOT RECOMMENDED / MISMATCH. "
            "This problem relies heavily on niche hardware, electrical testing standards, or defense signal theory. "
            "Our team's core superpowers (Scraping, React, UI/UX animations, AI full-stack) would be underutilized."
        )

    # Tech Stack suggestions
    tech_stack = []
    if "blockchain" in combined_text:
        tech_stack.extend(["Solidity", "Ethers.js", "Polygon/Sepolia Testnet", "IPFS"])
    if any(k in combined_text for k in ["gis", "land", "satellite", "spatial", "map"]):
        tech_stack.extend(["PostGIS", "Leaflet/Mapbox", "GeoServer", "Python GDAL/Shapely"])
    if any(k in combined_text for k in ["anpr", "vision", "camera", "detect", "image"]):
        tech_stack.extend(["YOLOv8", "OpenCV", "PyTorch", "FastAPI"])
    if any(k in combined_text for k in ["chatbot", "nlp", "llm", "advisory", "summariz"]):
        tech_stack.extend(["LangChain / LlamaIndex", "HuggingFace", "OpenAI/Gemini API", "ChromaDB / Qdrant"])
    
    # Standard base tech stack
    tech_stack.extend(["React.js", "Tailwind CSS", "Node.js / Express or FastAPI", "PostgreSQL / MongoDB", "Framer Motion", "Vercel / Docker"])
    tech_stack_str = ", ".join(list(dict.fromkeys(tech_stack))[:6])

    # Feasibility
    if diff_score <= 4.5 and ai_score >= 7.5:
        feasibility = "High (Demoable Working MVP in < 24 hrs)"
    elif diff_score <= 7.0 and ai_score >= 5.5:
        feasibility = "Moderate (High-Impact Demo achievable in 36 hrs)"
    elif diff_score <= 8.5:
        feasibility = "Challenging (Requires disciplined focus on MVP scope)"
    else:
        feasibility = "Low / Research Only (Difficult to prove in 36 hrs)"

    return {
        "diff_score": diff_score,
        "diff_level": diff_level,
        "diff_rationale": diff_rationale,
        "ai_score": ai_score,
        "ai_level": ai_level,
        "ai_rationale": ai_rationale,
        "team_score": team_score,
        "team_level": team_level,
        "team_strategy": strategy,
        "tech_stack": tech_stack_str,
        "feasibility": feasibility
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_CSV)
    output_csv_path = os.path.join(base_dir, OUTPUT_CSV)
    output_json_path = os.path.join(base_dir, OUTPUT_JSON)

    print(f"[+] Loading raw dataset from: {input_path}")
    if not os.path.exists(input_path):
        print(f"[!] File not found: {input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_records = list(reader)

    print(f"[+] Total records in source file: {len(all_records)}")

    # Filter strictly for Software category
    software_records = [r for r in all_records if r.get("Category", "").strip().lower() == "software"]
    print(f"[+] Filtered Software records: {len(software_records)}")

    processed_rows = []
    for r in software_records:
        bg, core_prob, exp_sol, full_cleaned = parse_sections(r.get("Full Description", ""))
        submitted_count, comp_level = parse_submission_count(r.get("Submitted Ideas Count", ""))

        analysis = analyze_statement(r)

        # External links collection
        yt = clean_text(r.get("YouTube Link", ""))
        ds = clean_text(r.get("Dataset Link", ""))
        contact = clean_text(r.get("Contact Info", ""))
        ext_links = []
        if yt: ext_links.append(f"YouTube: {yt}")
        if ds: ext_links.append(f"Dataset: {ds}")
        if contact: ext_links.append(f"Contact: {contact}")
        links_str = " | ".join(ext_links) if ext_links else "None"

        row = {
            "Our Team Fit Score (1-10)": analysis["team_score"],
            "Our Team Fit Level": analysis["team_level"],
            "Our Team Role & Strategy": analysis["team_strategy"],
            "Difficulty Score (1-10)": analysis["diff_score"],
            "Difficulty Level": analysis["diff_level"],
            "Difficulty Rationale": analysis["diff_rationale"],
            "AI Assistance Score (1-10)": analysis["ai_score"],
            "AI Assistance Level": analysis["ai_level"],
            "AI Assistance Rationale": analysis["ai_rationale"],
            "PS Number": r.get("PS Number", "").strip(),
            "Problem Statement ID": r.get("Problem Statement ID", "").strip(),
            "Title": clean_text(r.get("Title", "")),
            "Theme": clean_text(r.get("Theme", "")),
            "Organization": clean_text(r.get("Organization", "")),
            "Department": clean_text(r.get("Department", "")),
            "Key Tech Stack / Recommended Skills": analysis["tech_stack"],
            "Hackathon Feasibility": analysis["feasibility"],
            "Submitted Ideas Count": submitted_count,
            "Competition Level": comp_level,
            "Cleaned Background": bg,
            "Cleaned Core Problem": core_prob,
            "Cleaned Expected Solution": exp_sol,
            "Full Cleaned Description": full_cleaned,
            "Deadline": clean_text(r.get("Deadline", "")),
            "External Links": links_str
        }
        processed_rows.append(row)

    # Sort primarily by Our Team Fit Score descending (10 to 1), secondarily by Difficulty Score ascending
    processed_rows.sort(key=lambda x: (x["Our Team Fit Score (1-10)"], -x["Difficulty Score (1-10)"]), reverse=True)

    # Assign Our Team Fit Rank (1 to 178)
    for rank, row in enumerate(processed_rows, start=1):
        row["Our Team Fit Rank"] = rank

    # Write to CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_HEADERS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_rows:
            writer.writerow(row)

    print(f"[OK] Successfully exported {len(processed_rows)} ranked records to CSV: {output_csv_path}")

    # Write to JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(processed_rows, f, indent=2, ensure_ascii=False)

    print(f"[OK] Successfully exported {len(processed_rows)} ranked records to JSON: {output_json_path}")

    # Print Summary & Top 10 Recommendations
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY & TOP 10 RECOMMENDATIONS FOR YOUR TEAM:")
    print("="*80)
    print(f"Total Software Statements Processed: {len(processed_rows)}")
    
    jackpot_count = sum(1 for r in processed_rows if r["Our Team Fit Score (1-10)"] >= 8.8)
    strong_count = sum(1 for r in processed_rows if 7.5 <= r["Our Team Fit Score (1-10)"] < 8.8)
    viable_count = sum(1 for r in processed_rows if 5.5 <= r["Our Team Fit Score (1-10)"] < 7.5)
    avoid_count = sum(1 for r in processed_rows if r["Our Team Fit Score (1-10)"] < 5.5)

    print(f"\nTeam Fit Breakdown:")
    print(f"  - Jackpot Matches (8.8 - 10.0): {jackpot_count}")
    print(f"  - Strong Matches (7.5 - 8.7):  {strong_count}")
    print(f"  - Viable with Effort (5.5 - 7.4): {viable_count}")
    print(f"  - Low Fit / Avoid (< 5.5):     {avoid_count}")

    print("\n" + "-"*80)
    print("TOP 10 BEST MATCHES FOR YOUR TEAM (Scraping + React + High-end UI/UX + AI):")
    print("-"*80)
    for r in processed_rows[:10]:
        print(f"Rank #{r['Our Team Fit Rank']:02d} | Fit: {r['Our Team Fit Score (1-10)']}/10 | Diff: {r['Difficulty Score (1-10)']}/10 | AI: {r['AI Assistance Score (1-10)']}/10")
        print(f"       ID: {r['PS Number']} | Theme: {r['Theme']}")
        print(f"       Title: {r['Title'][:75]}...")
        print(f"       Ideas Submitted: {r['Submitted Ideas Count']} ({r['Competition Level']})")
        print()
    print("="*80)

if __name__ == "__main__":
    main()
