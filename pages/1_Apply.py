import streamlit as st
import anthropic
import requests
import os
import re
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

# ── RESUME DATA ───────────────────────────────────────────────────────

RESUME_TECHNICAL = """
EXPERIENCE:
- Founder, CareerTuners (Oct 2010 - Present): 3x'd service capacity in 2023 by integrating OpenAI API into service model and sales operations. Transitioned employees to franchise ownership in 2026 to reduce overhead. Double-digit % revenue growth YoY, 3 departments/CXOs, 30 staff, ~2.5x higher price point than industry benchmarks.
- Employment Services Provider, Eli Home + Casa Teresa Shelters (Oct 2023 - Present): Developing a RAG-based app using data matching and ML for real-time personalized coaching; won 2 TCVN pitch competitions; applying for grants. Co-authored "AI-Driven Interview Coaching Platform" paper; presented at SoCal + National Conferences of Undergraduate Research.
- Substitute Calculus Tutor, Mathinasium, 310Tutors (Nov 2025 - Present)

EDUCATION:
- UCLA, B.S. Mathematics of Computation (GPA: 3.6, expected Spring 2027)
- Scholarships: Glickfeld Scholarship, Visions of Unity Contest
- Coursework: Real Analysis (Honors), Algebra (Honors), Data Analysis, NLP, Machine Learning, Probabilistic Decision-Making, Neural Networks, Algorithm Design
- Technical Skills: LLM Integration, C++, Java, R, Python; Data Modeling; Data Visualization; Algorithm Analysis; Product Development and Management; P&L Analysis
- Activities: ACM AI (student participant); Directed Reading in logic and statistics

HACKATHONS:
- Image Classification (PyTorch, neural networks)
- Hurricane Response Dashboard (image/video generation, gMaps API)
- eColi Detection Hardware (supply chain analysis, market analysis)

OTHER:
- Public Speaking: CA State Championships, TedxPurdue, Guest Lecturer (CSUN, CSUF)
- 30,000+ LinkedIn followers; weekly career development lives
"""

RESUME_EXECUTIVE = """
EXPERIENCE:
Director of Customer Service / Training / Operations, CareerTuners (Oct 2010 - Present):
- Built marketing, operations, service, sales, and support departments from the ground up (completely virtual)
- HR: 30 offshore employees including 4 senior managers. 0 turnover during COVID recession.
- Finance: P&L, balance, and cash flow dashboards; company-wide ERP implementation
- Sales: Improved call conversions from 7% to 40%; reduced refund rates from 8% to 0.3%; customer spend $550 to $950
- Training: Built scalable "democratized" training programs; shortened onboarding cycles; SMART performance management
- Business Dev: ~$65K monthly revenue; 200K+ email sign-ups; organic traffic 40K hits/month; co-authored Amazon best-seller
- Franchise transition complete; automated personal workload to <2hrs/month
- RAG-based AI coaching app; 2 pitch competition wins; research paper at SoCal + National Conferences

EDUCATION:
- UCLA, B.S. Mathematics of Computation (GPA 3.6, expected Spring 2027) — returning student
- Previously completed 170 units toward B.Eng. Environmental Engineering at UCLA

SPEAKING / THOUGHT LEADERSHIP:
- TedxPurdue speaker; CA State Championships (debate, ranked #7 in CA); Guest Lecturer at CSUN, CSUF, UCLA
- 30,000+ LinkedIn followers; weekly career development live sessions
"""

COVER_LETTER_SENIOR = """
Fatemah Mirza
fatemah@g.ucla.edu | 951.284.5404 | Los Angeles, CA

To whom this letter may concern,

At first glance, my background presents a paradox: I am a founder who scaled a 30-person firm to double-digit growth, a Math student at UCLA tackling honors-level analysis, and a technical researcher building RAG-based applications for underserved communities.

While these chapters may seem disparate, they are driven by a singular focus that aligns perfectly with [COMPANY]'s mission: [MISSION_ALIGNMENT]

I am applying for the [ROLE] because I have spent the last decade and a half navigating the exact [RELEVANT_DOMAIN]. At CareerTuners, I spearheaded [CAREERTUNRS_RELEVANCE]. I learned firsthand that [KEY_LESSON].

Why I am a unique fit for the [TEAM] team:

• [BULLET_1]

• [BULLET_2]

• [BULLET_3]

I have recently transitioned CareerTuners to a franchise-ownership model. By automating the operational core of the business, I have reduced my personal workload to under two hours a month, allowing me to bring 100% of my focus and energy to this role at [COMPANY].

Best regards,

Fatemah Mirza
951.284.5404 | fatemah@g.ucla.edu
"""

COVER_LETTER_INTERN = """
Fatemah Mirza
fatemah@g.ucla.edu | 951.284.5404 | Los Angeles, CA

To whom this letter may concern,

I am writing to apply for the [ROLE] at [COMPANY]. I am a Mathematics of Computation student at UCLA (GPA: 3.6) with hands-on experience in [RELEVANT_SKILLS], and I am excited by the specific work this role involves: [ROLE_SPECIFIC_APPEAL].

[ROLE_BODY_PARAGRAPH: 2-3 sentences connecting her most relevant technical experience directly to what this role requires. Be specific — name actual tools, methods, or projects.]

Why I would hit the ground running in this role:

• [BULLET_1]

• [BULLET_2]

• [BULLET_3]

I would welcome the opportunity to contribute to [TEAM_OR_PROJECT] and learn from your team. Thank you for your consideration.

Best regards,

Fatemah Mirza
951.284.5404 | fatemah@g.ucla.edu
"""

# ── HELPERS ───────────────────────────────────────────────────────────

def call_claude(prompt, max_tokens=1500):
    system = """You are a writing assistant. Follow these rules strictly:
- Never use markdown formatting (no **, no __, no ##, no bullet dashes)
- Never use em dashes (—). Use a comma, period, or rewrite the sentence instead.
- Never use en dashes (–)
- Use plain punctuation only: commas, periods, colons, semicolons
- Write in clean, natural prose that sounds human
- Use hyphens only in compound words (e.g. well-known)"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def parse_job_info_dict(job_info_text):
    info = {}
    for line in job_info_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            info[key.strip()] = val.strip()
    return info


def is_intern_level(job_info_dict):
    return job_info_dict.get("SENIORITY", "").lower() in ("intern", "junior", "entry")


def load_approved_examples(folder):
    examples = []
    if os.path.exists(folder):
        for fname in sorted(os.listdir(folder)):
            fpath = os.path.join(folder, fname)
            with open(fpath, "r") as f:
                examples.append(f"--- Example: {fname} ---\n{f.read()}")
    return "\n\n".join(examples) if examples else ""


def save_output(folder, filename, content):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "w") as f:
        f.write(content)


# ── EMAIL FINDER ──────────────────────────────────────────────────────

def extract_domain_from_jd(company):
    """Ask Claude to guess the company domain."""
    result = call_claude(f"""What is the most likely corporate email domain for a company called "{company}"?

Important rules:
- If this is a subsidiary or division of a larger company, return the PARENT company domain
- Examples: "Assa Abloy Opening Solutions" -> assaabloy.com, "Google DeepMind" -> google.com, "Amazon Web Services" -> amazon.com
- Return ONLY the domain, nothing else, e.g. assaabloy.com""", max_tokens=50)
    return result.strip().lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")


def hunter_domain_search(domain):
    """Search Hunter.io for emails at a domain."""
    try:
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}&limit=5"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        emails = data.get("data", {}).get("emails", [])
        pattern = data.get("data", {}).get("pattern", "")
        return emails, pattern
    except Exception:
        return [], ""


def hunter_email_finder(first, last, domain):
    """Use Hunter's Email Finder to find a specific person's email."""
    try:
        url = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first}&last_name={last}&api_key={HUNTER_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        email = data.get("data", {}).get("email")
        score = data.get("data", {}).get("score", 0)
        return email, score
    except Exception:
        return None, 0


def find_decision_maker_email(job_info_dict):
    company = job_info_dict.get("COMPANY", "")
    role    = job_info_dict.get("ROLE", "")
    track   = job_info_dict.get("TRACK", "technical")
    seniority = job_info_dict.get("SENIORITY", "mid")

    # Step 1: Ask Claude who to contact
    dm = call_claude(f"""For this job, who should a candidate address a cold outreach email to?

Company: {company}
Role: {role}
Track: {track}
Seniority: {seniority}

Return in EXACTLY this format:
NAME: <first and last name, or Unknown>
TITLE: <their likely title>
WHY: <one sentence on why they are the right person>
SEARCH: <exact search string for LinkedIn or RocketReach>
FIRST: <just their first name>
LAST: <just their last name>""", max_tokens=300)

    dm_dict = {}
    for line in dm.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            dm_dict[k.strip()] = v.strip()

    first = dm_dict.get("FIRST", "")
    last  = dm_dict.get("LAST", "")
    name  = dm_dict.get("NAME", "Hiring Manager")

    # Step 2: Try Hunter.io
    domain = extract_domain_from_jd(company)
    emails, pattern = hunter_domain_search(domain)

    # Try to match by name in domain search results
    matched_email = None
    for e in emails:
        full = ((e.get("first_name") or "") + " " + (e.get("last_name") or "")).lower()
        if last.lower() and last.lower() in full:
            matched_email = e.get("value")
            break

    # Step 3: Try Email Finder directly if no match yet
    guessed_email = None
    if not matched_email and first and last and first.lower() != "unknown":
        found_email, score = hunter_email_finder(first, last, domain)
        if found_email and score >= 50:
            matched_email = found_email  # high confidence — treat as verified
        elif found_email:
            guessed_email = found_email  # low confidence — flag it

    # Step 4: Fall back to pattern guess
    if not matched_email and not guessed_email and pattern and first and last:
        guessed_email = pattern.replace("{first}", first.lower()).replace("{last}", last.lower()) + f"@{domain}"

    return {
        "name": name,
        "title": dm_dict.get("TITLE", ""),
        "why": dm_dict.get("WHY", ""),
        "search": dm_dict.get("SEARCH", ""),
        "domain": domain,
        "matched_email": matched_email,
        "guessed_email": guessed_email,
        "pattern": pattern,
        "raw": dm,
    }


# ── GENERATORS ────────────────────────────────────────────────────────

def extract_job_info(jd):
    return call_claude(f"""Extract from this job description and return in EXACTLY this format:

COMPANY: <company name>
ROLE: <exact job title>
TRACK: <technical or executive>
TEAM: <team or department, or Not specified>
LOCATION: <city state, or Not specified>
MISSION: <one sentence what this company does>
KEY_SKILLS: <3-5 skills comma separated>
DOMAIN: <core problem space, short phrase>
SENIORITY: <intern / junior / mid / senior / director / VP / C-level>

Job description:
{jd}""")


def tailor_resume(jd, job_info, track):
    resume = RESUME_TECHNICAL if track == "technical" else RESUME_EXECUTIVE
    approved = load_approved_examples("approved_examples/resumes")
    style = f"\n\nPast approved examples to match:\n{approved}" if approved else ""
    return call_claude(f"""Tailor Fatemah Mirza's resume for this job.

Resume: {resume}
Job info: {job_info}
Job description: {jd}
{style}

1. Reorder bullets — most relevant first
2. Mark suggested edits with [SUGGESTED EDIT]
3. Mark cuts with [CONSIDER REMOVING] + reason
4. Keep her authentic voice
5. IMPORTANT: Even if this is an intern role, do not soften or omit her real experience.
   She is a non-traditional candidate — her C-level background, LLM integration work, and
   UCLA technical coursework are all directly relevant and should be prominently featured.
   Match her actual experience to the role requirements explicitly.
Output full tailored resume as plain text.""")


def write_cover_letter(jd, job_info, job_info_dict, track):
    resume = RESUME_TECHNICAL if track == "technical" else RESUME_EXECUTIVE
    approved = load_approved_examples("approved_examples/cover_letters")
    style = f"\n\nPast approved examples:\n{approved}" if approved else ""
    template = COVER_LETTER_INTERN if is_intern_level(job_info_dict) else COVER_LETTER_SENIOR
    tone = """INTERN ROLE — tone guidance:
    - No grand mission statements or company vision language
    - Focus on the specific role requirements
    - BUT: do not water down her experience. She has 15 years of real operator and technical experience. Use it.
    - Match her actual background directly to what the role needs
    - Do not default to junior framing. She is a non-traditional candidate with more experience than most full-time hires.""" if is_intern_level(job_info_dict) else "SENIOR ROLE: Use full founder narrative, connect to company mission."
    return call_claude(f"""{tone}

Fill in this cover letter template:
{template}

Resume: {resume}
Job info: {job_info}
Job description: {jd}
{style}

Fill every placeholder. Keep her voice. No fake experience. Output only the finished letter.""")


def write_cover_email(jd, job_info, job_info_dict, manager_name, cover_letter):
    resume = RESUME_TECHNICAL if "executive" not in job_info_dict.get("TRACK", "").lower() else RESUME_EXECUTIVE
    is_intern = is_intern_level(job_info_dict)
    tone = "This is an intern/junior role but the candidate has 15 years of real operator and technical experience. Do NOT write junior-sounding bullets. Match the role requirements directly to her actual experience — she has done equivalent work at a much higher level." if is_intern else "Senior role — reference her founder and operator background directly."

    return call_claude(f"""{tone}

Write a cold outreach email for Fatemah Mirza.

Structure:
---
Subject: Interest in [ROLE] at [COMPANY]

Hi [MANAGER],

My name is Fatemah Mirza and I wanted to express my interest in the [ROLE] at [COMPANY].

Highlights of my background that align with this role:
- [BULLET 1]
- [BULLET 2]
- [BULLET 3]

If possible, I'd be grateful if you could point me to the hiring manager or relevant head to further explore how I might contribute to your team's success. (And if you'd like to take a look at my resume, I can also share that.)

Thank you so much for reading, and I look forward to the possibility of connecting.

Warm regards,
Fatemah Mirza
951.284.5404
---

Job info: {job_info}
Manager: {manager_name}

Her actual background to draw bullets from:
{resume}

Cover letter for additional context:
{cover_letter}

RULES FOR BULLETS:
- Draw ONLY from her actual background above — no invention
- Each bullet must directly match a specific requirement from the job description
- Use her real experience: C-level operations, Python/R, LLM integration, data pipelines, RAG app, UCLA coursework in ML/algorithms/data analysis
- Do not soften or junior-ify her experience just because the role title says intern
- Name specific tools, projects, or outcomes she actually has
- Three bullets maximum, one sentence each

Job description for matching:
{jd}

Output only the finished email.""")


def salary_estimate(job_info_dict):
    return call_claude(f"""Realistic salary range for:
Role: {job_info_dict.get('ROLE')}
Seniority: {job_info_dict.get('SENIORITY')}
Location: {job_info_dict.get('LOCATION', 'Los Angeles CA')}
Skills: {job_info_dict.get('KEY_SKILLS')}

Candidate has 15 years founder/operator experience, UCLA Math of Computation GPA 3.6, LLM integration experience. Needs $70K+/year after tax for part-time/fractional, or $35/hr+ for internships.

Return EXACTLY:
SALARY_RANGE: $X - $Y (type)
NEGOTIATION_NOTE: <one sentence>
TAX_NOTE: <one sentence CA take-home>""", max_tokens=300)


# ── MAIN PAGE ─────────────────────────────────────────────────────────

st.set_page_config(page_title="Apply", page_icon="📄", layout="wide")
st.title("📄 Apply")

# Mode selector
st.markdown("### What do you need?")
options = st.multiselect(
    "",
    [
        "A — Resume",
        "B — Cover Letter",
        "C — Cover Email",
        "D — Decision Maker + Email Finder",
    ],
    default=["A — Resume", "B — Cover Letter", "C — Cover Email", "D — Decision Maker + Email Finder"],
    label_visibility="collapsed"
)
mode_keys = [o[0] for o in options]

st.markdown("---")

# Job description input
jd = st.text_area("Paste the job description here", height=250, placeholder="Paste full job description...")

# Manager override
manager_override = st.text_input("Override decision-maker name (optional — leave blank to auto-detect)", placeholder="e.g. Dr. Morgan Chen")

col_run, col_clear = st.columns([1, 1])
with col_run:
    run = st.button("🚀 Run", type="primary", use_container_width=True)
with col_clear:
    if st.button("🔄 Start Over", use_container_width=True):
        st.rerun()

if run and jd.strip():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Always extract job info first
    with st.spinner("Analyzing job description..."):
        job_info      = extract_job_info(jd)
        job_info_dict = parse_job_info_dict(job_info)
        track         = "executive" if "executive" in job_info_dict.get("TRACK", "").lower() else "technical"
        company       = job_info_dict.get("COMPANY", "company").lower().replace(" ", "_")
        folder        = f"applications/{company}_{timestamp}"

    with st.expander("📋 Extracted Job Info", expanded=False):
        st.code(job_info)

    # ── Mode A: Everything ──
    if "A" in mode_keys:
        progress = st.progress(0, text="Analyzing job description...")
        with concurrent.futures.ThreadPoolExecutor() as ex:
            f_resume = ex.submit(tailor_resume, jd, job_info, track) if need_resume else None
            f_letter = ex.submit(write_cover_letter, jd, job_info, job_info_dict, track) if need_letter or need_email else None
            f_salary = ex.submit(salary_estimate, job_info_dict) if need_resume else None
            f_dm     = ex.submit(find_decision_maker_email, job_info_dict) if need_dm else None

            progress.progress(10, text="Documents generating in parallel...")

            resume_out = f_resume.result() if f_resume else None
            progress.progress(40, text="Resume done...")

            letter_out = f_letter.result() if f_letter else None
            progress.progress(65, text="Cover letter done...")

            salary_out = f_salary.result() if f_salary else None
            progress.progress(80, text="Salary note done...")

            dm = f_dm.result() if f_dm else None
            progress.progress(90, text="Decision maker found...")

        manager_name = (manager_override or dm["name"]) if dm else "Hiring Manager"
        email_out = write_cover_email(jd, job_info, job_info_dict, manager_name, letter_out or "") if need_email else None
        progress.progress(100, text="Done!")

        # Display
        st.markdown("### 🎯 Decision Maker")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{dm['name']}** — {dm['title']}")
            st.caption(dm['why'])
            if dm['matched_email']:
                st.success(f"✅ Verified email: `{dm['matched_email']}`")
            elif dm['guessed_email']:
                st.warning(f"⚠️ Guessed email: `{dm['guessed_email']}` — verify on Hunter.io")
            else:
                st.info(f"No email found. Search: `{dm['search']}`")
        with col2:
            st.markdown(f"**RocketReach / LinkedIn search:**")
            st.code(dm['search'])

        st.markdown("### 💰 Salary Note")
        st.info(salary_out)

        st.markdown("### 📝 Tailored Resume")
        st.text_area("", resume_out, height=400, key="resume")

        st.markdown("### 📄 Cover Letter")
        st.text_area("", letter_out, height=400, key="letter")

        st.markdown("### ✉️ Cover Email")
        st.text_area("", email_out, height=300, key="email")

        # Save all
        save_output(folder, "job_info.txt", job_info)
        save_output(folder, "resume.txt", resume_out)
        save_output(folder, "cover_letter.txt", letter_out)
        save_output(folder, "cover_email.txt", email_out)
        save_output(folder, "salary_note.txt", salary_out)
        save_output(folder, "decision_maker.txt", dm['raw'])
        st.success(f"✅ All files saved to `{folder}/`")

    # ── Mode B: Cover letter ──
    if "B" in mode_keys:
        with st.spinner("Writing cover letter..."):
            letter_out = write_cover_letter(jd, job_info, job_info_dict, track)
        st.markdown("### 📄 Cover Letter")
        st.text_area("", letter_out, height=400, key="letter")
        save_output(folder, "cover_letter.txt", letter_out)
        st.success(f"✅ Saved to `{folder}/cover_letter.txt`")

    # ── Mode C: Cover email ──
# ── Mode C: Cover email ──
    if "C" in mode_keys:
        with st.spinner("Finding decision maker..."):
            dm = find_decision_maker_email(job_info_dict)
        manager_name = manager_override or dm["name"]
        # use letter_out if B was also selected, else empty
        letter_for_email = letter_out if "B" in mode_keys else ""
        with st.spinner("Writing cover email..."):
            email_out = write_cover_email(jd, job_info, job_info_dict, manager_name, letter_for_email)
        st.markdown("### ✉️ Cover Email")
        st.text_area("", email_out, height=300, key="email")
        save_output(folder, "cover_email.txt", email_out)
        st.success(f"✅ Saved to `{folder}/cover_email.txt`")

    # ── Mode D: Decision maker + email finder ──
    if "D" in mode_keys:
        with st.spinner("Finding decision maker and email..."):
            dm = find_decision_maker_email(job_info_dict)
        manager_name = manager_override or dm["name"]

        st.markdown("### 🎯 Decision Maker")
        st.markdown(f"**{dm['name']}** - {dm['title']}")
        st.caption(dm['why'])

        if dm['matched_email']:
            st.success(f"Verified email: {dm['matched_email']}")
        elif dm['name'] != "Unknown" and dm['guessed_email'] and "unknown" not in dm['guessed_email'].lower():
            st.warning(f"Guessed email: {dm['guessed_email']} - verify on Hunter.io before sending")
        else:
            hunter_link = f"https://hunter.io/search/{dm['domain']}?filter_seniority=executive,director,manager&filter_department=engineering,it"
            hunter_link_dm = f"https://hunter.io/search/{dm['domain']}?tab=decision_makers"
            st.info("No specific email found automatically.")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"[Hunter.io - Decision Makers]({hunter_link_dm})")
                st.markdown(f"[Hunter.io - Engineering/IT]({hunter_link})")
            with col_b:
                st.markdown(f"[LinkedIn Search](https://www.linkedin.com/search/results/people/?keywords={dm['search'].replace(' ', '%20')})")
                st.markdown(f"[RocketReach](https://rocketreach.co/search?keyword={dm['search'].replace(' ', '+')})")

        st.markdown("Search string:")
        st.code(dm['search'])
        st.markdown(f"Company domain: {dm['domain']}")
        if dm['pattern']:
            st.markdown(f"Email pattern: {dm['pattern']}")

        save_output(folder, "decision_maker.txt", dm['raw'])
        st.success(f"✅ Saved to `{folder}/decision_maker.txt`")

        # if C was also selected, now write the email using the DM we just found
        if "C" in mode_keys and "email_out" not in dir():
            letter_for_email = letter_out if "B" in mode_keys else ""
            with st.spinner("Writing cover email..."):
                email_out = write_cover_email(jd, job_info, job_info_dict, manager_name, letter_for_email)
            st.markdown("### ✉️ Cover Email")
            st.text_area("", email_out, height=300, key="email")
            save_output(folder, "cover_email.txt", email_out)
            st.success(f"✅ Saved to `{folder}/cover_email.txt`")


    # ── Feedback section ──
    st.markdown("---")
    st.markdown("### 💾 Save Edits for Future Learning")
    st.caption("If you edited any output above, paste it back here to improve future results.")
    fb_type = st.selectbox("Which output did you edit?", ["— skip —", "resume", "cover_letter", "email"])
    fb_content = st.text_area("Paste your edited version here", height=200)
    if st.button("Save to Approved Examples") and fb_type != "— skip —" and fb_content.strip():
        folder_map = {
            "resume": "approved_examples/resumes",
            "cover_letter": "approved_examples/cover_letters",
            "email": "approved_examples/emails",
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_output(folder_map[fb_type], f"{ts}_{fb_type}.txt", fb_content)
        st.success("Saved! Future runs will reference this.")

elif run and not jd.strip():
    st.error("Please paste a job description first.")