from dotenv import load_dotenv
import os
import anthropic
from datetime import datetime

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── PROFILE SUMMARIES ─────────────────────────────────────────────────

PROFILE_TECHNICAL = """
Fatemah Mirza — Technical Track
- UCLA Mathematics of Computation student, GPA 3.6, expected Spring 2027
- LLM integration (OpenAI API, RAG), Python, C++, Java, R
- ML, NLP, Neural Networks, Algorithm Design coursework
- Built RAG-based coaching app; hackathons in image classification (PyTorch), dashboard dev, hardware
- Research: co-authored AI coaching paper, presented at SoCal + National Conferences
- CareerTuners: automated service operations using LLMs, 3x'd capacity
- Seeking: internship or part-time technical role (software, ML, automation, internal tools)
- Location: Los Angeles, CA — open to hybrid or remote
"""

PROFILE_EXECUTIVE = """
Fatemah Mirza — Executive/Fractional Track
- 15 years operating CareerTuners: 30 staff, double-digit YoY revenue growth, ~$65K/month revenue
- P&L, cash flow, ERP; tied finance KPIs to department metrics
- Built sales, training, and ops departments from ground up; 0 turnover during COVID
- Improved sales conversions 7%→40%, reduced refund rates 8%→0.3%
- Franchise transition complete; automated personal workload to <2hrs/month
- TedxPurdue speaker; 30K LinkedIn followers; guest lecturer
- Seeking: fractional CMO, COO, Chief of Staff, or Head of Operations — part-time, $70K+ after tax equivalent
- Location: Los Angeles, CA — open to remote
"""

SEARCH_QUERIES = {
    "technical": [
        "software automation intern Los Angeles 2026",
        "ML engineering intern UCLA student Los Angeles",
        "LLM AI intern part-time Los Angeles hybrid",
        "software engineering intern site:wellfound.com",
        "automation tools developer intern Python Los Angeles",
    ],
    "executive": [
        "fractional CMO Los Angeles startup 2026",
        "fractional COO remote part-time",
        "fractional Chief of Staff startup remote",
        "part-time VP Operations AI startup",
        "site:fractionaljobs.io CMO COO operations",
        "site:gofractional.com fractional executive marketing operations",
    ]
}

def call_claude(prompt, max_tokens=2000):
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def call_claude_with_search(prompt, max_tokens=2000):
    """Call Claude with web search tool enabled."""
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    # Collect all text blocks from the response
    result = []
    for block in response.content:
        if hasattr(block, "text"):
            result.append(block.text)
    return "\n".join(result).strip()

def save_output(folder, filename, content):
    os.makedirs(folder, exist_ok=True)
    fpath = os.path.join(folder, filename)
    with open(fpath, "w") as f:
        f.write(content)
    print(f"  Saved: {fpath}")

def search_jobs(track):
    profile = PROFILE_TECHNICAL if track == "technical" else PROFILE_EXECUTIVE
    queries = SEARCH_QUERIES[track]

    print(f"\nSearching for {track} roles...")
    print("(This may take 30-60 seconds — Claude is searching the web)\n")

    query_list = "\n".join(f"- {q}" for q in queries)

    prompt = f"""You are a job search assistant helping Fatemah Mirza find roles that fit her profile.

Her profile:
{profile}

Please search the web using these queries to find currently open, real job postings:
{query_list}

Also search these specific boards which are most relevant for her:
{"- Handshake (for UCLA students), Wellfound, Indeed, LinkedIn" if track == "technical" else "- fractionaljobs.io, gofractional.com, bolster.co, LinkedIn"}

Return a list of 5-10 real, currently open job postings. For each one include:

ROLE: [job title]
COMPANY: [company name]
LINK: [direct URL to the job posting if found, otherwise company careers page]
POSTED: [date posted if visible, else "unknown"]
FIT NOTE: [one sentence explaining specifically why this matches Fatemah's background]
SALARY: [if listed, otherwise "not listed"]

Only include real postings you find — do not make up roles.
If a board has no current relevant listings, skip it.
Rank results by fit quality, best match first."""

    return call_claude_with_search(prompt)

def combine_tracks(technical_results, executive_results):
    return call_claude(f"""Fatemah Mirza is looking at both technical internships and fractional executive roles.

Here are search results for both tracks:

--- TECHNICAL RESULTS ---
{technical_results}

--- EXECUTIVE/FRACTIONAL RESULTS ---
{executive_results}

Please combine these into one clean ranked list of the top 10 most promising roles overall.
For each, keep: ROLE, COMPANY, LINK, FIT NOTE, SALARY.
Add a TRACK label (Technical / Executive) to each.
Remove any duplicates.
Rank by overall fit and opportunity quality.""")

def main():
    print("=" * 50)
    print("   Job Search Tool — Fatemah Mirza")
    print("=" * 50)

    print("""
Which track do you want to search?
  1. Technical  (internships, software, ML, automation)
  2. Executive  (fractional CMO/COO/Chief of Staff)
  3. Both
""")
    choice = input("> ").strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder    = f"job_searches/{timestamp}"

    if choice == "1":
        results = search_jobs("technical")
        print(f"\n\n{'='*50}\nTECHNICAL ROLE RESULTS\n{'='*50}")
        print(results)
        save_output(folder, "technical_roles.txt", results)

    elif choice == "2":
        results = search_jobs("executive")
        print(f"\n\n{'='*50}\nEXECUTIVE/FRACTIONAL ROLE RESULTS\n{'='*50}")
        print(results)
        save_output(folder, "executive_roles.txt", results)

    elif choice == "3":
        tech_results = search_jobs("technical")
        exec_results = search_jobs("executive")

        print("\nCombining and ranking all results...")
        combined = combine_tracks(tech_results, exec_results)

        print(f"\n\n{'='*50}\nALL RESULTS — RANKED BY FIT\n{'='*50}")
        print(combined)

        save_output(folder, "technical_roles.txt", tech_results)
        save_output(folder, "executive_roles.txt",  exec_results)
        save_output(folder, "combined_ranked.txt",  combined)
    else:
        print("Invalid choice. Please run again and enter 1, 2, or 3.")
        return

    print(f"\nResults saved to: {folder}/")
    print("\nTo apply to any of these roles, copy the job description and run: python main.py")

if __name__ == "__main__":
    main()
