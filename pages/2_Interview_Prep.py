import streamlit as st
import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESUME_TECHNICAL = """
- Founder, CareerTuners: 3x'd service capacity via OpenAI API integration; franchise transition 2026
- Employment Services: RAG-based coaching app (ML, data matching); 2 pitch competition wins; co-authored research paper
- UCLA Mathematics of Computation, GPA 3.6; ML, NLP, Neural Networks, Algorithm Design
- Technical Skills: LLM Integration, Python, C++, Java, R; Data Modeling; Algorithm Analysis
- Hackathons: Image Classification (PyTorch), Hurricane Response Dashboard, eColi Detection Hardware
"""

RESUME_EXECUTIVE = """
- Founder/Director, CareerTuners: 30 staff, 4 senior managers, double-digit YoY revenue growth
- P&L, cash flow, ERP implementation; finance KPIs tied to department metrics
- Sales: conversions 7%→40%; refund rates 8%→0.3%; customer spend $550→$950
- Training programs for sales, marketing, content, clerical from scratch
- ~$65K monthly revenue; 200K+ email sign-ups; organic traffic 40K hits/month
- Franchise transition; automated to <2hrs/month personal workload
- RAG-based AI coaching app; pitch competition wins; research paper published
- TedxPurdue; 30K LinkedIn followers; guest lecturer CSUN/CSUF/UCLA
"""

def call_claude(prompt, max_tokens=2000):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def load_approved_examples():
    folder = "approved_examples/interview_notes"
    examples = []
    if os.path.exists(folder):
        for fname in sorted(os.listdir(folder)):
            with open(os.path.join(folder, fname)) as f:
                examples.append(f"--- {fname} ---\n{f.read()}")
    return "\n\n".join(examples) if examples else ""

def save_output(folder, filename, content):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "w") as f:
        f.write(content)

# ── PAGE ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Interview Prep", page_icon="🎯", layout="wide")
st.title("🎯 Interview Prep")
st.caption("Paste interviewer LinkedIn bios to get personalized coaching notes")

col1, col2 = st.columns(2)
with col1:
    role    = st.text_input("Role you're interviewing for", placeholder="e.g. Software Automation Intern")
    company = st.text_input("Company", placeholder="e.g. Mission Microwave")
with col2:
    track = st.radio("Resume track", ["technical", "executive"])

interviewers = st.text_area(
    "Paste interviewer info here",
    height=300,
    placeholder="Names, titles, LinkedIn bios, recent posts, anything you have...\n\nExample:\nDr. Morgan Chen — VP Engineering\n[paste their LinkedIn about section, recent posts, etc.]"
)

run = st.button("🎯 Generate Coaching Notes", type="primary")

if run and interviewers.strip() and role and company:
    resume = RESUME_TECHNICAL if track == "technical" else RESUME_EXECUTIVE
    approved = load_approved_examples()
    style = f"\n\nPast approved examples to match in style:\n{approved}" if approved else ""

    with st.spinner("Analyzing interviewers..."):
        notes = call_claude(f"""You are an expert interview coach helping Fatemah Mirza prepare for a job interview.

Role: {role}
Company: {company}

Interviewer info:
{interviewers}

Fatemah's background:
{resume}
{style}

For EACH interviewer, write coaching notes:
- Name and title
- What they seem to care about based on background and language
- Potential hesitations or concerns about Fatemah specifically
- 2-4 specific talking points tailored to this person
- Personal signals worth noting (posts, volunteer work, career quirks)
- If info is thin, say so and give general guidance by title

Be direct, honest, practical — like a coach 30 minutes before the interview.
Flag real risks, not just positives.""", max_tokens=2000)

    st.markdown("### 📋 Coaching Notes")
    st.text_area("", notes, height=500, key="notes")

    # Save
    company_slug = company.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"applications/{company_slug}_interview_{timestamp}"
    save_output(folder, "interview_notes.txt", notes)
    st.success(f"✅ Saved to `{folder}/interview_notes.txt`")

    # Feedback
    st.markdown("---")
    st.markdown("### 💾 Save Edits for Future Learning")
    edited = st.text_area("If you edited the notes, paste your version here", height=200)
    if st.button("Save to Approved Examples") and edited.strip():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_output("approved_examples/interview_notes", f"{ts}_notes.txt", edited)
        st.success("Saved!")

elif run:
    st.error("Please fill in role, company, and interviewer info.")
