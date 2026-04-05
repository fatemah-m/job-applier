from dotenv import load_dotenv
import os
import anthropic
from datetime import datetime

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESUME_TECHNICAL = """
- Founder, CareerTuners: 3x'd service capacity via OpenAI API integration; franchise transition 2026
- Employment Services: RAG-based coaching app (ML, data matching); 2 pitch competition wins; co-authored research paper presented at SoCal + National Conferences of Undergraduate Research
- UCLA Mathematics of Computation, GPA 3.6; ML, NLP, Neural Networks, Algorithm Design coursework
- Technical Skills: LLM Integration, Python, C++, Java, R; Data Modeling; Algorithm Analysis
- Hackathons: Image Classification (PyTorch), Hurricane Response Dashboard, eColi Detection Hardware
"""

RESUME_EXECUTIVE = """
- Founder/Director, CareerTuners: 30 staff, 4 senior managers, double-digit YoY revenue growth
- P&L, cash flow, ERP implementation; tied finance KPIs to department metrics
- Sales: conversions 7%→40%; refund rates 8%→0.3%; customer spend $550→$950
- Training programs for sales, marketing, content, clerical teams from scratch
- ~$65K monthly revenue; 200K+ email sign-ups; organic traffic 40K hits/month
- Franchise transition complete; automated to <2hrs/month personal workload
- RAG-based AI coaching app; pitch competition wins; research paper published
- TedxPurdue; 30K LinkedIn followers; guest lecturer CSUN/CSUF/UCLA
"""

def call_claude(prompt, max_tokens=2000):
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def paste_multiline(prompt):
    print(prompt)
    print("(Type END on a new line when done)\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()

def load_approved_examples():
    folder = "approved_examples/interview_notes"
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

def analyze_interviewers(interviewers_raw, role, company, track):
    resume = RESUME_TECHNICAL if track == "technical" else RESUME_EXECUTIVE
    approved = load_approved_examples()
    style_note = f"\n\nHere are past approved interview coaching notes to match in style and depth:\n{approved}" if approved else ""

    return call_claude(f"""You are an expert interview coach helping Fatemah Mirza prepare for a job interview.

Role: {role}
Company: {company}

Interviewer info (LinkedIn bios, posts, titles, anything provided):
{interviewers_raw}

Fatemah's background:
{resume}
{style_note}

For EACH interviewer mentioned, write coaching notes in this exact style:

[Name] — [Title]
- What they seem to care about based on their background, language, and activity
- Potential hesitations or concerns they might have about Fatemah specifically
- 2-4 specific talking points tailored to this person
- Any personal signals (posts, volunteer work, career path) worth noting
- If their info is thin, say so briefly and give general guidance based on their title

Be direct, honest, and practical — like a coach giving notes 30 minutes before the interview.
Flag real risks, not just positives. Be as specific as the information allows.""")

def main():
    print("=" * 50)
    print("   Interview Prep Tool — Fatemah Mirza")
    print("=" * 50)

    role    = input("\nWhat role are you interviewing for? ").strip()
    company = input("What company? ").strip()

    print("\nWhat track? (technical / executive)")
    track = input("> ").strip().lower()
    if track not in ("technical", "executive"):
        track = "technical"

    interviewers_raw = paste_multiline(
        "\nPaste interviewer info below (names, titles, LinkedIn bios, posts, anything you have)."
    )

    if not interviewers_raw:
        print("No interviewer info provided. Exiting.")
        return

    print("\nAnalyzing interviewers...")
    notes = analyze_interviewers(interviewers_raw, role, company, track)

    print(f"\n\n{'='*50}\nINTERVIEWER COACHING NOTES\n{'='*50}")
    print(notes)

    # Save
    company_slug = company.lower().replace(" ", "_")
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder       = f"applications/{company_slug}_interview_{timestamp}"
    save_output(folder, "interview_notes.txt", notes)

    # Feedback loop
    print("\nDid you edit these notes? Paste back to save as approved example. (y/n)")
    if input("> ").strip().lower() == "y":
        edited = paste_multiline("Paste your edited notes below.")
        if edited:
            save_output("approved_examples/interview_notes", f"{timestamp}_notes.txt", edited)
            print("Saved! Future runs will reference this.")

    print(f"\nDone! Notes saved to: {folder}/")

if __name__ == "__main__":
    main()
