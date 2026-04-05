import streamlit as st

st.set_page_config(
    page_title="Job Application Tool — Fatemah Mirza",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Job Application Tool")
st.caption("Powered by Claude AI + Hunter.io")

st.markdown("""
Use the sidebar to navigate between tools:

- **📄 Apply** — Tailored resume, cover letter, outreach email, and decision-maker finder
- **🎯 Interview Prep** — Personalized coaching notes based on interviewer LinkedIn profiles
- **🔍 Job Search** — Find roles that match your profile across technical and executive tracks
""")

st.info("👈 Select a tool from the sidebar to get started.")
