from dotenv import load_dotenv
import os
import anthropic
from datetime import datetime
import concurrent.futures

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── RESUME DATA ───────────────────────────────────────────────────────

RESUME_TECHNICAL = """
EXPERIENCE:
- Founder, CareerTuners (Oct 2010 - Present): 3x'd service capacity in 2023 by integrating OpenAI API into service model and sales operations. Transitioned employees to franchise ownership in 2026 to reduce overhead. Double-digit % revenue growth YoY, 3 departments/CXOs, 30 staff, ~2.5x higher price point than industry benchmarks.
- Employment Services Provider, Eli Home + Casa Teresa Shelters (Oct 2023 - Present): Developing a RAG-based app using data matching and ML for real-time personalized coaching; won 2 TCVN pitch competitions; applying for grants. Co-authored "AI-Driven Interview Coaching Platform" paper; presented at SoCal + National Conferences of Undergraduate Research. Collecting/refining qualitative data using iterative feedback loop.
- Substitute Calculus Tutor, Mathinasium, 310Tutors (Nov 2025 - Present)

EDUCATION:
- UCLA, B.S. Mathematics of Computation (GPA: 3.6, expected Spring 2027)
- Scholarships: Glickfeld Scholarship, Visions of Unity Contest
- Coursework: Real Analysis (Honors), Algebra (Honors), Data Analysis, NLP, Machine Learning, Probabilistic Decision-Making, Neural Networks, Algorithm Design
- Technical Skills: LLM Integration, C++, Java, R, Python; Data Modeling; Data Visualization; Algorithm Analysis; Product Development and Management; P&L Analysis
- Activities: ACM AI (student participant); Directed Reading in logic and statistics (decision-making, optimization, network theory, ML)

HACKATHONS:
- Image Classification (PyTorch, neural networks)
- Hurricane Response Dashboard (image/video generation, gMaps API)
- eColi Detection Hardware (supply chain analysis, market analysis)

OTHER:
- Public Speaking: CA State Championships, TedxPurdue, Guest Lecturer (CSUN, CSUF)
- Hindi/Urdu Poetry (Fluent); Conversational in Spanish, Malayalam
- 30,000+ LinkedIn followers; weekly career development lives
"""

RESUME_EXECUTIVE = """
EXPERIENCE:
Director of Customer Service / Training / Operations, CareerTuners (Oct 2010 - Present):
- Built marketing, operations, service, sales, and support departments from the ground up (completely virtual)
- HR: 30 offshore employees including 4 senior managers. Improved payroll competitiveness while doubling revenue via KPI-tied financials. 0 turnover during COVID recession.
- Finance: P&L, balance, and cash flow dashboards; company-wide ERP implementation; tied finance KPIs to department metrics
- Sales: Improved call conversions from 7% to 40%; reduced refund rates from 8% to 0.3%; improved total customer spend from $550 to $950
- Training: Built scalable "democratized" training programs for sales, marketing, content, clerical; shortened onboarding cycles; SMART performance management frameworks
- Business Dev: ~$65K monthly revenue; 200K+ email sign-ups; organic traffic to 40K hits/month; co-authored Amazon best-seller career guide; doubled LCV
- Currently transitioning company to franchise model; automated operational core to under 2 hours/month personal workload
- Developing AI coaching app (RAG-based); won 2 TCVN pitch competitions; co-authored research paper; presented at SoCal + National Conferences of Undergraduate Research

EDUCATION:
- UCLA, B.S. Mathematics of Computation (GPA 3.6, expected Spring 2027) — returning student
- Previously completed 170 units toward B.Eng. Environmental Engineering at UCLA
- Coursework: ML, NLP, Neural Networks, Algorithm Design, Real Analysis (Honors), Probabilistic Decision-Making

SPEAKING / THOUGHT LEADERSHIP:
- TedxPurdue speaker; CA State Championships (debate, ranked #7 in CA); Guest Lecturer at CSUN, CSUF, UCLA
- 30,000+ LinkedIn followers; weekly career development live sessions
- Delivered career coaching workshops across US (CA, MI, IL, FL) and Pakistan (FAST, NUST, LUMS)
"""

# Two cover letter templates depending on seniority level
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

[ROLE_BODY_PARAGRAPH: 2-3 sentences connecting her most relevant technical experience directly to what this role requires. Be specific — name actual tools, methods, or projects. No mission statements, no founder narrative. Just: here is what the role needs, here is where I have done that.]

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
    fpath = os.path.join(folder, filename)
    with open(fpath, "w") as f:
        f.write(content)
    print(f"  Saved: {fpath}")


def paste_multiline(prompt):
    print(prompt)
    print("(Type END on a new line when done, or just END to skip)\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def parse_job_info_dict(job_info_text):
    info = {}
    for line in job_info_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            info[key.strip()] = val.strip()
    return info


def is_intern_level(job_info_dict):
    seniority = job_info_dict.get("SENIORITY", "").lower()
    return seniority in ("intern", "junior", "entry")


# ── STEP 1: EXTRACT JOB INFO ──────────────────────────────────────────

def extract_job_info(job_description):
    print("\n[1/4] Analyzing job description...")
    return call_claude(f"""From this job description, extract the following and return in EXACTLY this format with no extra text:

COMPANY: <company name>
ROLE: <exact job title>
TRACK: <either "technical" or "executive" — technical if engineering/software/data/research, executive if management/leadership/operations/C-suite/fractional>
TEAM: <team or department name if mentioned, else "Not specified">
LOCATION: <city, state if mentioned, else "Not specified">
MISSION: <one sentence describing what this company does or cares about>
KEY_SKILLS: <3-5 most important skills or themes the role needs, comma separated>
DOMAIN: <the core problem space this role works in, one short phrase>
SENIORITY: <intern / junior / mid / senior / director / VP / C-level>

Job description:
{job_description}""")


# ── STEP 2: TAILOR RESUME ─────────────────────────────────────────────

def tailor_resume(job_description, job_info, track):
    print("[2/4] Tailoring resume...")
    resume = RESUME_TECHNICAL if track == "technical" else RESUME_EXECUTIVE
    approved = load_approved_examples("approved_examples/resumes")
    style_note = f"\n\nHere are past approved resume outputs to match in style and tone:\n{approved}" if approved else ""

    return call_claude(f"""You are helping Fatemah Mirza tailor her resume for a specific job.

Her full resume content:
{resume}

Job info:
{job_info}

Job description:
{job_description}
{style_note}

Instructions:
1. Reorder and select the most relevant bullets — lead with what matches the role best
2. Suggest 1-2 edits to existing bullets if a small rewrite would make them land harder (mark with [SUGGESTED EDIT])
3. Flag any bullet to cut as [CONSIDER REMOVING] with a one-line reason
4. Keep her authentic voice — do not add skills she doesn't have
5. Output the full tailored resume as plain text, ready to paste

Output the resume now.""")


# ── STEP 3: COVER LETTER ──────────────────────────────────────────────

def write_cover_letter(job_description, job_info, job_info_dict, track):
    print("[3/4] Writing cover letter...")
    resume = RESUME_TECHNICAL if track == "technical" else RESUME_EXECUTIVE
    approved = load_approved_examples("approved_examples/cover_letters")
    style_note = f"\n\nHere are past approved cover letters to match in style and tone:\n{approved}" if approved else ""

    # Pick template based on seniority
    if is_intern_level(job_info_dict):
        template = COVER_LETTER_INTERN
        tone_instruction = """IMPORTANT TONE NOTE: This is an intern/entry-level role.
- Do NOT reference company mission in a grand way — it reads as pompous at this level
- Focus purely on the role itself: what it requires, and where her background matches
- Keep it grounded, specific, and role-focused
- The ROLE_BODY_PARAGRAPH should name actual tools/methods/projects, not abstract qualities
- No founder narrative unless directly relevant to a specific skill the role needs"""
    else:
        template = COVER_LETTER_SENIOR
        tone_instruction = """This is a senior/executive role. Use her full founder narrative.
Connect her background to the company's mission and the team's goals."""

    return call_claude(f"""You are filling in Fatemah Mirza's cover letter template for a specific job.

{tone_instruction}

Template to fill in (replace ALL bracketed placeholders):
{template}

Her resume background:
{resume}

Job info extracted:
{job_info}

Full job description:
{job_description}
{style_note}

Fill in every placeholder with specific, compelling content. Keep her authentic voice.
Do not add fake experience. Output only the finished cover letter, nothing else.""")


# ── STEP 4: COVER EMAIL ───────────────────────────────────────────────

def write_cover_email(job_description, job_info, job_info_dict, manager_name, cover_letter):
    print("[4/4] Writing cover email...")

    if is_intern_level(job_info_dict):
        tone_note = "This is an intern role — keep the email grounded and role-focused. No grand mission statements."
    else:
        tone_note = "This is a senior role — she can reference her founder background briefly."

    return call_claude(f"""You are writing a short cold outreach email for Fatemah Mirza.

{tone_note}

Use this exact structure:
---
Subject: Interest in [ROLE] at [COMPANY]

Hi [MANAGER],

My name is Fatemah Mirza and I wanted to express my interest in the [ROLE] at [COMPANY].

Highlights of my background that align with this role include the following:
- [BULLET 1: one sentence]
- [BULLET 2: one sentence]
- [BULLET 3: one sentence]

If possible, I'd be grateful if you could point me to the hiring manager or relevant head to further explore how I might contribute to your team's success. (And if you'd like to take a look at my resume, I can also share that.)

Thank you so much for reading, and I look forward to the possibility of connecting.

Warm regards,
Fatemah Mirza
951.284.5404
---

Job info: {job_info}
Manager to address: {manager_name}
Cover letter bullets to draw from: {cover_letter}

Output only the finished email, nothing else.""")


# ── SALARY ESTIMATE ───────────────────────────────────────────────────

def salary_estimate(job_info_dict):
    role      = job_info_dict.get("ROLE", "this role")
    seniority = job_info_dict.get("SENIORITY", "mid")
    location  = job_info_dict.get("LOCATION", "Los Angeles, CA")
    track     = job_info_dict.get("TRACK", "technical")
    skills    = job_info_dict.get("KEY_SKILLS", "")

    return call_claude(f"""Give a realistic salary/pay range for this role. Be specific and direct.

Role: {role}
Seniority: {seniority}
Location: {location}
Track: {track}
Key skills: {skills}

The candidate has 15 years of founder/operator experience, is a returning UCLA student (GPA 3.6, Math of Computation), and has LLM integration experience. She needs at least $70K/year after taxes for part-time or fractional work, or $35/hr+ for internships/hourly roles.

Return in EXACTLY this format:
SALARY_RANGE: $X - $Y (note whether full-time / part-time / hourly / internship stipend)
NEGOTIATION_NOTE: <one sentence on whether she should push higher, and why>
TAX_NOTE: <one sentence on approximate CA take-home at the low and high end>""")


# ── FEEDBACK LOGGER ───────────────────────────────────────────────────

def log_feedback():
    print("\n── Save Edits for Future Learning ──")
    print("Did you edit any output? Paste it back to save as an approved example.")
    print("Which file? (resume / cover_letter / email / skip)")
    choice = input("> ").strip().lower()

    if choice in ("skip", ""):
        return

    type_map = {
        "resume":       "approved_examples/resumes",
        "cover_letter": "approved_examples/cover_letters",
        "email":        "approved_examples/emails",
    }

    if choice not in type_map:
        print("Unrecognized choice, skipping.")
        return

    content = paste_multiline(f"Paste your edited {choice} below.")
    if not content:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_output(type_map[choice], f"{timestamp}_{choice}.txt", content)
    print("Saved! Future runs will reference this.")


# ── MAIN ──────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("   Job Application Generator — Fatemah Mirza")
    print("=" * 50)

    job_description = paste_multiline("\nPaste the job description below.")
    if not job_description:
        print("No job description provided. Exiting.")
        return

    print("\nLooking up suggested decision-maker...")
    dm_suggestion = call_claude(f"""For this job, who should a candidate address a cold outreach email to?

Job info:
{job_info}

Return in EXACTLY this format:
NAME: <first and last name, or "Unknown">
TITLE: <their likely title>
WHY: <one sentence on why they are the right person to contact>
SEARCH: <exact search string to use on LinkedIn or RocketReach to find them>
EMAIL_GUESS: <guessed email based on firstname.lastname@domain.com pattern, note to verify>""")

    print("\n── Suggested Decision-Maker ──")
    print(dm_suggestion)
    save_output(folder, "decision_maker.txt", dm_suggestion)

    manager_name = input("\nWho should the email be addressed to? (press Enter to use suggestion, or type a name): ").strip()
    if not manager_name:
        # extract NAME from suggestion
        for line in dm_suggestion.splitlines():
            if line.startswith("NAME:"):
                manager_name = line.replace("NAME:", "").strip()
                break
    if not manager_name or manager_name == "Unknown":
        manager_name = "Hiring Manager"

    # ── Pipeline ──
    job_info      = extract_job_info(job_description)
    print("\n── Extracted Job Info ──")
    print(job_info)

    job_info_dict = parse_job_info_dict(job_info)
    track         = "executive" if "executive" in job_info_dict.get("TRACK", "").lower() else "technical"
    level         = job_info_dict.get("SENIORITY", "mid")
    print(f"\n── Track: {track.upper()} | Level: {level.upper()} ──")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f_resume   = executor.submit(tailor_resume, job_description, job_info, track)
        f_letter   = executor.submit(write_cover_letter, job_description, job_info, job_info_dict, track)
        f_salary   = executor.submit(salary_estimate, job_info_dict)
        resume_out       = f_resume.result()
        cover_letter_out = f_letter.result()
        salary_out       = f_salary.result()

    email_out = write_cover_email(job_description, job_info, job_info_dict, manager_name, cover_letter_out)

    # ── Save ──
    company   = job_info_dict.get("COMPANY", "company").lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder    = f"applications/{company}_{timestamp}"

    print(f"\n── Saving to {folder}/ ──")
    save_output(folder, "job_info.txt",     job_info)
    save_output(folder, "resume.txt",       resume_out)
    save_output(folder, "cover_letter.txt", cover_letter_out)
    save_output(folder, "cover_email.txt",  email_out)
    save_output(folder, "salary_note.txt",  salary_out)

    # ── Print ──
    for title, content in [
        ("RESUME",       resume_out),
        ("COVER LETTER", cover_letter_out),
        ("COVER EMAIL",  email_out),
        ("SALARY NOTE",  salary_out),
    ]:
        print(f"\n\n{'='*50}\n{title}\n{'='*50}")
        print(content)

    print(f"\n💡 Run interview_prep.py separately to build interviewer coaching notes.")

    log_feedback()
    print(f"\nAll done! Files saved to: {folder}/")


if __name__ == "__main__":
    main()
