"""
SIH 2026: Automated Notion Workspace Setup Script
Populates the parent page with:
1. Executive Header & Mission Callout
2. Team Roster & Roles Matrix
3. Sprint Kanban Database (Pre-seeded with Operation APIx tasks)
4. Milestone Checkpoints Database (SIH 2026 Calendar)
5. 6-Slide Official SIH PPT Specification Guide
6. 36-Hour Grand Finale War Room Checklist
"""

import sys
import json
import time
import urllib.request
import urllib.error

# Ensure UTF-8 output encoding for Windows PowerShell / CMD
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ.get("NOTION_TOKEN", "your_notion_token_here")
PARENT_PAGE_ID = "3d571437-089c-8095-9b9d-f68b62013d87"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def make_request(url, method="POST", data=None):
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[-] HTTP {e.code} Error on {url}: {err_msg}")
        return None
    except Exception as e:
        print(f"[-] Request Error: {e}")
        return None

def append_dashboard_blocks(page_id):
    print("[*] Adding Executive Dashboard blocks to parent page...")
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    blocks = [
        # Callout block
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "🏆 Operation APIx: Real-Time Airfare Price Index for India\n"},
                        "annotations": {"bold": True}
                    },
                    {
                        "type": "text",
                        "text": {"content": "SIH 2026 Problem Statement: "},
                        "annotations": {"bold": True}
                    },
                    {
                        "type": "text",
                        "text": {"content": "SIH26056 (Ministry of Statistics & Programme Implementation - MoSPI)\n"}
                    },
                    {
                        "type": "text",
                        "text": {"content": "🚨 MANDATORY RULE: Every team must have 6 members with at least 1 female teammate. An all-male team will be disqualified by the portal/SPOC!"},
                        "annotations": {"color": "red"}
                    }
                ],
                "icon": {"emoji": "✈️"},
                "color": "blue_background"
            }
        },
        # Divider
        {"object": "block", "type": "divider", "divider": {}},
        # Heading 2: Quick Links & Team Mission
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📌 Quick Navigation & Team Hub"}}]
            }
        },
        # Bulleted items
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "🎯 Objective: "}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Replace MoSPI's outdated manual once-a-month airfare surveys with a high-frequency automated scraping and DGCA-weighted Laspeyres index platform."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "👥 Team Composition: "}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Lead (Scraping & Full-Stack) | Sukesh (React & Backend) | Shivam (UI/UX) | Yash (Pitch & Strategy) | Slot 5 (Mandatory Female) | Slot 6 (Domain Researcher)"}}
                ]
            }
        },
        # Toggle 1: Official SIH PPT 6-Slide Template
        {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [
                    {"type": "text", "text": {"content": "📑 Official SIH 6-Slide PPT Template Specification (Click to Expand)"}, "annotations": {"bold": True}}
                ],
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": "• Slide 1: Title, Team ID, Problem Statement ID (SIH26056), Institute Code & SPOC.\n• Slide 2: Problem Understanding (CPI Base 2024=100 revision, dynamic surge blind spots).\n• Slide 3: Proposed Solution (Stealth scrapers, unbundled fares, Laspeyres index engine).\n• Slide 4: Technical Architecture (Playwright, FastAPI, PostgreSQL, React Dashboard, RBI API).\n• Slide 5: Feasibility & Viability (Anti-bot evasion, 36-hour sprint plan, risk mitigations).\n• Slide 6: Impact & Scalability (National inflation accuracy, RBI monetary policy support)."}}]
                        }
                    }
                ]
            }
        },
        # Toggle 2: 36-Hour Hackathon Survival Blueprint
        {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [
                    {"type": "text", "text": {"content": "⏱️ 36-Hour Grand Finale Survival Mechanics (Click to Expand)"}, "annotations": {"bold": True}}
                ],
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": "• Mentoring Round 1 (Day 1 Morning): Listen actively, note all mentor suggestions on whiteboard.\n• Evaluation Round 1 (Day 1 Evening): Show running database, API endpoints, and clean Git commits.\n• Mentoring Round 2 (Day 2 Night): Prove you implemented Round 1 feedback (judges score this heavily!).\n• Evaluation Round 2 (Day 2 Morning): Demonstrate complete end-to-end user journey with offline fallbacks.\n• Power Round (Day 2 Afternoon): 5-minute live working demo + 3-minute jury Q&A."}}]
                        }
                    }
                ]
            }
        },
        {"object": "block", "type": "divider", "divider": {}}
    ]

    resp = make_request(url, "PATCH", {"children": blocks})
    if resp:
        print("[+] Successfully added Executive Dashboard blocks!")
    return resp

def create_tasks_database(parent_page_id):
    print("[*] Creating '⚡ Sprint Tasks & Deliverables' Database in Notion...")
    url = "https://api.notion.com/v1/databases"
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "⚡ Sprint Tasks & Deliverables (Kanban)"}}],
        "properties": {
            "Task Name": {"title": {}},
            "Assignee": {
                "select": {
                    "options": [
                        {"name": "Lead (You)", "color": "purple"},
                        {"name": "Sukesh", "color": "blue"},
                        {"name": "Shivam", "color": "orange"},
                        {"name": "Yash", "color": "green"},
                        {"name": "Slot 5 (Female - Mandatory)", "color": "pink"},
                        {"name": "Slot 6 (Domain Researcher)", "color": "yellow"},
                        {"name": "Entire Team", "color": "default"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "📋 Backlog", "color": "default"},
                        {"name": "⏳ In Progress", "color": "blue"},
                        {"name": "👀 Under Review", "color": "yellow"},
                        {"name": "✅ Completed", "color": "green"}
                    ]
                }
            },
            "Priority": {
                "select": {
                    "options": [
                        {"name": "🔴 Critical", "color": "red"},
                        {"name": "🟡 High", "color": "yellow"},
                        {"name": "🟢 Medium", "color": "green"}
                    ]
                }
            },
            "Phase": {
                "select": {
                    "options": [
                        {"name": "Phase 1: College Screening", "color": "orange"},
                        {"name": "Phase 2: Idea PPT Submission", "color": "purple"},
                        {"name": "Phase 3: Core Scraper & Engine", "color": "blue"},
                        {"name": "Phase 4: MoSPI Dashboard", "color": "green"},
                        {"name": "Phase 5: Grand Finale", "color": "red"}
                    ]
                }
            },
            "Due Date": {"date": {}}
        }
    }
    
    db = make_request(url, "POST", payload)
    if not db:
        print("[-] Failed to create tasks database.")
        return None
        
    db_id = db["id"]
    print(f"[+] Tasks Database created successfully! (ID: {db_id})")
    
    initial_tasks = [
        {
            "name": "🚨 Recruit Female Teammate (Mandatory for SIH Qualification)",
            "assignee": "Entire Team",
            "status": "⏳ In Progress",
            "priority": "🔴 Critical",
            "phase": "Phase 1: College Screening",
            "due": "2026-09-12"
        },
        {
            "name": "Connect with College SPOC & Register for Internal Hackathon",
            "assignee": "Yash",
            "status": "⏳ In Progress",
            "priority": "🔴 Critical",
            "phase": "Phase 1: College Screening",
            "due": "2026-09-15"
        },
        {
            "name": "Draft 6-Slide Official SIH Idea PPT (Export to PDF)",
            "assignee": "Yash",
            "status": "⏳ In Progress",
            "priority": "🔴 Critical",
            "phase": "Phase 2: Idea PPT Submission",
            "due": "2026-09-20"
        },
        {
            "name": "Build Python Stealth Scraper Prototype (Playwright + Network Intercept)",
            "assignee": "Lead (You)",
            "status": "⏳ In Progress",
            "priority": "🟡 High",
            "phase": "Phase 3: Core Scraper & Engine",
            "due": "2026-09-22"
        },
        {
            "name": "Implement Laspeyres Price Index Formula with DGCA Weights",
            "assignee": "Lead (You)",
            "status": "📋 Backlog",
            "priority": "🟡 High",
            "phase": "Phase 3: Core Scraper & Engine",
            "due": "2026-09-25"
        },
        {
            "name": "Design MoSPI Intelligence Command Center UI in Figma",
            "assignee": "Shivam",
            "status": "⏳ In Progress",
            "priority": "🟡 High",
            "phase": "Phase 4: MoSPI Dashboard",
            "due": "2026-09-22"
        },
        {
            "name": "Build React Flight Heatmap & Inflation Velocity Components",
            "assignee": "Sukesh",
            "status": "📋 Backlog",
            "priority": "🟡 High",
            "phase": "Phase 4: MoSPI Dashboard",
            "due": "2026-09-28"
        },
        {
            "name": "Pre-seed Database with 30-Day Historical Indian City-Pair Data",
            "assignee": "Sukesh",
            "status": "📋 Backlog",
            "priority": "🟢 Medium",
            "phase": "Phase 3: Core Scraper & Engine",
            "due": "2026-10-05"
        },
        {
            "name": "Package Full Offline Demo Stack in Docker / Localhost Fallback",
            "assignee": "Lead (You)",
            "status": "📋 Backlog",
            "priority": "🔴 Critical",
            "phase": "Phase 5: Grand Finale",
            "due": "2026-11-20"
        }
    ]
    
    print("[*] Pre-populating tasks into database...")
    for t in initial_tasks:
        page_payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Task Name": {"title": [{"text": {"content": t["name"]}}]},
                "Assignee": {"select": {"name": t["assignee"]}},
                "Status": {"select": {"name": t["status"]}},
                "Priority": {"select": {"name": t["priority"]}},
                "Phase": {"select": {"name": t["phase"]}},
                "Due Date": {"date": {"start": t["due"]}}
            }
        }
        make_request("https://api.notion.com/v1/pages", "POST", page_payload)
        time.sleep(0.3)
        
    print("[+] All initial tasks populated!")
    return db_id

def create_milestones_database(parent_page_id):
    print("[*] Creating '🗓️ SIH 2026 Official Checkpoints & Roadmap' Database...")
    url = "https://api.notion.com/v1/databases"
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "🗓️ SIH 2026 Official Checkpoints & Roadmap"}}],
        "properties": {
            "Checkpoint": {"title": {}},
            "Window / Date": {"rich_text": {}},
            "Stage": {
                "select": {
                    "options": [
                        {"name": "College Round", "color": "orange"},
                        {"name": "National Screening", "color": "purple"},
                        {"name": "Mentoring & Build", "color": "blue"},
                        {"name": "Grand Finale", "color": "red"}
                    ]
                }
            },
            "Key Deliverable": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "🔥 Active Now", "color": "red"},
                        {"name": "Upcoming", "color": "yellow"},
                        {"name": "Future Milestone", "color": "gray"}
                    ]
                }
            }
        }
    }
    
    db = make_request(url, "POST", payload)
    if not db:
        print("[-] Failed to create milestones database.")
        return None
        
    db_id = db["id"]
    print(f"[+] Milestones Database created successfully! (ID: {db_id})")
    
    milestones = [
        {
            "name": "1. College Internal Hackathon & SPOC Quota Selection",
            "date": "September 2026 (Ongoing)",
            "stage": "College Round",
            "deliverable": "College shortlist (Top 45 teams) + 6-member team quota entry by SPOC",
            "status": "🔥 Active Now"
        },
        {
            "name": "2. National Idea Submission Deadline",
            "date": "Late Sep / Early Oct 2026",
            "stage": "National Screening",
            "deliverable": "Official 6-Slide Idea PPT (PDF) + Executive Abstract uploaded by SPOC",
            "status": "Upcoming"
        },
        {
            "name": "3. Ministry (MoSPI) Central Evaluation & Scoring",
            "date": "October – November 2026",
            "stage": "National Screening",
            "deliverable": "Blind evaluation by MoSPI domain judges; scoring on innovation, feasibility, impact",
            "status": "Upcoming"
        },
        {
            "name": "4. Grand Finale Finalist Announcement & Nodal Assignment",
            "date": "Mid–Late November 2026",
            "stage": "Mentoring & Build",
            "deliverable": "Top 4–6 teams per PS shortlisted nationally; ticket booking (2nd Sleeper reimbursed)",
            "status": "Future Milestone"
        },
        {
            "name": "5. The 36-Hour Grand Finale (Non-Stop Offline Hackathon)",
            "date": "December 2026",
            "stage": "Grand Finale",
            "deliverable": "Working Prototype, Live API Sandbox, Jury Defense, ₹1,00,000 Award Evaluation",
            "status": "Future Milestone"
        }
    ]
    
    for m in milestones:
        page_payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Checkpoint": {"title": [{"text": {"content": m["name"]}}]},
                "Window / Date": {"rich_text": [{"text": {"content": m["date"]}}]},
                "Stage": {"select": {"name": m["stage"]}},
                "Key Deliverable": {"rich_text": [{"text": {"content": m["deliverable"]}}]},
                "Status": {"select": {"name": m["status"]}}
            }
        }
        make_request("https://api.notion.com/v1/pages", "POST", page_payload)
        time.sleep(0.3)
        
    print("[+] All milestones populated!")
    return db_id

if __name__ == "__main__":
    print("==================================================")
    print("🚀 Auto-Configuring SIH 2026 Notion Workspace")
    print(f"Parent Page ID: {PARENT_PAGE_ID}")
    print("==================================================")
    
    append_dashboard_blocks(PARENT_PAGE_ID)
    create_tasks_database(PARENT_PAGE_ID)
    create_milestones_database(PARENT_PAGE_ID)
    
    print("\n🎉 ALL DONE! Open your Notion page to view the live workspace:")
    print(f"👉 https://app.notion.com/p/SIH-2026-Operation-APIx-{PARENT_PAGE_ID}")
