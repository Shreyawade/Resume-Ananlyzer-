import streamlit as st
import pdfplumber
import json
import time
import re
import os
from io import BytesIO
from groq import Groq

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide"
)

# ✅ GET API KEY FROM ENV (IMPORTANT)
api_key = os.environ.get("GROK_API_KEY")

# ─────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


def analyze_resumes(resumes, job_description):
    client = Groq(api_key=api_key)

    resume_block = ""
    for i, (name, text) in enumerate(resumes.items(), 1):
        resume_block += f"\n\n--- RESUME {i}: {name} ---\n{text[:3000]}"

    prompt = f"""
Analyze resumes vs job description.

JOB DESCRIPTION:
{job_description}

RESUMES:
{resume_block}

Return JSON:
{{
  "ranked_candidates": [
    {{
      "rank": 1,
      "name": "",
      "overall_score": 85,
      "match_level": "Excellent",
      "matched_skills": [],
      "missing_skills": [],
      "strengths": [],
      "improvement_suggestions": []
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```.*?```", "", raw, flags=re.DOTALL)

    return json.loads(raw)


# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────
st.title("🎯 AI Resume Analyzer")

job_description = st.text_area("📋 Job Description")

uploaded_files = st.file_uploader(
    "📤 Upload 3–5 resumes (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🚀 Analyze"):

    errors = []

    if not api_key:
        errors.append("❌ API key not found. Set GROK_API_KEY in Render.")

    if not uploaded_files or not (3 <= len(uploaded_files) <= 5):
        errors.append("❌ Upload 3–5 resumes")

    if not job_description:
        errors.append("❌ Enter job description")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Extract text
    resumes = {}
    for f in uploaded_files:
        resumes[f.name] = extract_text_from_pdf(f)

    # Analyze
    with st.spinner("Analyzing..."):
        result = analyze_resumes(resumes, job_description)

    st.success("✅ Done!")

    # Display results
    for c in result.get("ranked_candidates", []):
        st.subheader(f"{c['rank']}️⃣ {c['name']}")
        st.write(f"Score: {c['overall_score']}%")
        st.write(f"Match: {c['match_level']}")

        st.write("✅ Matched Skills:", c["matched_skills"])
        st.write("❌ Missing Skills:", c["missing_skills"])

        st.write("💪 Strengths:")
        for s in c["strengths"]:
            st.write("-", s)

        st.write("💡 Improvements:")
        for s in c["improvement_suggestions"]:
            st.write("-", s)

        st.markdown("---")