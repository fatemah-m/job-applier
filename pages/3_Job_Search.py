import streamlit as st
import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROFILE_TECHNICAL = """
Fatemah Mirza — Technical Track
- UCLA Mathematics of Computation, GPA 3.6, expected Spring 2027
- LLM integration (OpenAI API, RAG), Python, C++, Java, R
- ML, NLP, Neural Networks, Algorithm Design coursework
- Built RAG-based coaching app; hackathons in image classification, dashboard dev, hardware
- Research: co-authored AI coaching paper, presented at SoCal + National Conferences
- CareerTuners: automated service operations using LLMs, 3x'd capacity
- Seeking: internship or part-time technical role (software, ML, automation, internal tools)
- Location: Los Angeles, CA — open to hybrid or remote
"""

PROFILE_EXECUTIVE = """
Fatemah Mirza — Executive/Fractional Track
- 15 years operating CareerTuners: 30 staff, double-digit YoY revenue growth, ~$65K/month
- P&L, cash flow, ERP; finance KPIs tied to department metrics
- Built sales, training, and ops departments from ground up; 0 turnover during COVID
- Sales conversions 7%→40%; refund rates 8%→0.3%
- Franchise transition complete; automated to <2hrs/month personal workload
- TedxPurdue speaker; 30K LinkedIn followers; guest lecturer
- Seeking: fractional CMO, COO, Chief of Staff — part-time, $70K+ after tax equivalent
- Location: Los Angeles, CA — open to remote
"""

def search_jobs(track):
    profile = PROFILE_TECHNICAL if track == "technical" else PROFILE_EXECUTIVE
    boards = "LinkedIn, Handshake (UCLA), Wellfound, Indeed" if track == "technical" else "fractionaljobs.io, gofractional.com, bolster.co, LinkedIn"
    queries = {
        "technical": [
            "software automation intern Los Angeles 2026",
            "ML engineering intern UCLA student Los Angeles",
            "LLM AI intern part-time Los Angeles hybrid",
            "automation tools developer intern Python Los Angeles",
        ],
        "executive": [
            "fractional CMO Los Angeles startup 2026",
            "fractional COO remote part-time",
            "fractional Chief of Staff startup remote",
            "part-time VP Operations AI startup",
        ]
    }

    query_list = "\n".join(f"- {q}" for q in queries[track])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": f"""You are a job search assistant helping Fatemah Mirza find roles.

Her profile:
{profile}

Search the web using these queries:
{query_list}

Also search these boards: {boards}

Return 5-10 real, currently open job postings. For each:

ROLE: [title]
COMPANY: [company]
LINK: [URL]
POSTED: [date or unknown]
FIT NOTE: [one sentence why this matches her background]
SALARY: [if listed, else not listed]

Only real postings. Rank by fit quality."""}]
    )

    result = []
    for block in response.content:
        if hasattr(block, "text"):
            result.append(block.text)
    return "\n".join(result).strip()

def save_output(folder, filename, content):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "w") as f:
        f.write(content)

# ── PAGE ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Job Search", page_icon="🔍", layout="wide")
st.title("🔍 Job Search")
st.caption("Find roles that match your profile — powered by live web search")

track_choice = st.radio(
    "Which track?",
    [
        "A — Technical (internships, software, ML, automation)",
        "B — Executive/Fractional (CMO, COO, Chief of Staff)",
        "C — Both",
    ]
)
track_key = track_choice[0]

run = st.button("🔍 Search Now", type="primary")

if run:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"job_searches/{timestamp}"

    if track_key == "A":
        with st.spinner("Searching for technical roles... (this takes ~30-60 seconds)"):
            results = search_jobs("technical")
        st.markdown("### 💻 Technical Roles")
        st.markdown(results)
        save_output(folder, "technical_roles.txt", results)
        st.success(f"✅ Saved to `{folder}/technical_roles.txt`")

    elif track_key == "B":
        with st.spinner("Searching for fractional/executive roles..."):
            results = search_jobs("executive")
        st.markdown("### 👔 Executive / Fractional Roles")
        st.markdown(results)
        save_output(folder, "executive_roles.txt", results)
        st.success(f"✅ Saved to `{folder}/executive_roles.txt`")

    elif track_key == "C":
        col1, col2 = st.columns(2)

        with col1:
            with st.spinner("Searching technical roles..."):
                tech = search_jobs("technical")
            st.markdown("### 💻 Technical Roles")
            st.markdown(tech)
            save_output(folder, "technical_roles.txt", tech)

        with col2:
            with st.spinner("Searching executive roles..."):
                exec_ = search_jobs("executive")
            st.markdown("### 👔 Executive / Fractional Roles")
            st.markdown(exec_)
            save_output(folder, "executive_roles.txt", exec_)

        st.success(f"✅ Both saved to `{folder}/`")

    st.markdown("---")
    st.info("👈 To apply to any role, copy the job description and head to the **Apply** page.")
