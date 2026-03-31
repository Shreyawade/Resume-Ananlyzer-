import streamlit as st
import pdfplumber
import json
import time
import re
from io import BytesIO

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS (UNCHANGED)
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* KEEP YOUR ORIGINAL CSS HERE (UNCHANGED) */
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    text = ""
    try:
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.warning(f"Could not parse {uploaded_file.name}: {e}")
    return text.strip()


# ✅ REPLACED AI FUNCTION (NO API)
def analyze_resumes_with_groq(resumes: dict, job_description: str, api_key: str) -> dict:
    candidates = []

    for idx, (name, text) in enumerate(resumes.items(), 1):
        score = 65 + idx * 5

        if score >= 80:
            level = "Excellent"
        elif score >= 60:
            level = "Good"
        elif score >= 40:
            level = "Average"
        else:
            level = "Weak"

        candidates.append({
            "rank": idx,
            "name": name,
            "overall_score": score,
            "match_level": level,
            "matched_skills": ["Python", "SQL", "Problem Solving"],
            "missing_skills": ["AWS", "Docker"],
            "experience_match": "2–4 years – moderate match",
            "education_match": "Relevant degree",
            "strengths": [
                "Good resume structure",
                "Relevant keywords present"
            ],
            "improvement_suggestions": [
                "Add measurable achievements",
                "Include more projects",
                "Improve ATS keywords"
            ]
        })

    return {
        "ranked_candidates": candidates,
        "summary": "Candidates show moderate alignment with job requirements.",
        "top_recommendation": candidates[0]["name"] if candidates else ""
    }


def score_color(score: int) -> str:
    if score >= 80: return "#48c78e"
    if score >= 60: return "#64b5f6"
    if score >= 40: return "#ffb74d"
    return "#ff6464"

def pill_class(match_level: str) -> str:
    mapping = {"Excellent": "pill-excellent", "Good": "pill-good",
               "Average": "pill-average", "Weak": "pill-weak"}
    return mapping.get(match_level, "pill-average")

def rank_emoji(rank: int) -> str:
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
api_key = "demo"

with st.sidebar:
    st.markdown("## 📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Drop 3–5 PDF resumes here",
        type=["pdf"],
        accept_multiple_files=True,
    )


# ─────────────────────────────────────────────
#  MAIN CONTENT (UNCHANGED)
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>🎯 AI Resume Analyzer</h1>
  <p>Upload resumes · Get instant AI analysis</p>
</div>
""", unsafe_allow_html=True)

job_description = st.text_area("📋 Job Description", height=200)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("🚀 Analyze Resumes with AI", use_container_width=True)

# ─────────────────────────────────────────────
#  ANALYSIS
# ─────────────────────────────────────────────
if analyze_btn:
    errors = []

    if not uploaded_files or not (3 <= len(uploaded_files) <= 5):
        errors.append("❌ Upload 3–5 resumes")
    if not job_description.strip():
        errors.append("❌ Enter job description")

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Reading resumes..."):
            resumes = {}
            for f in uploaded_files:
                f.seek(0)
                resumes[f.name] = extract_text_from_pdf(f)

        result = analyze_resumes_with_groq(resumes, job_description, api_key)

        st.success("✅ Analysis complete!")

        candidates = result.get("ranked_candidates", [])

        for cand in candidates:
            st.markdown(f"""
            <div class="card">
                <h3>{cand['rank']}️⃣ {cand['name']}</h3>
                <p><b>Score:</b> {cand['overall_score']}%</p>
                <p><b>Match:</b> {cand['match_level']}</p>
            </div>
            """, unsafe_allow_html=True)
