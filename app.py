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
#  CUSTOM CSS (RESTORED)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #f0f0f0;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

.card {
    background: rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
}
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


# ✅ DUMMY ANALYSIS (API REMOVED ONLY)
def analyze_resumes_with_groq(resumes: dict, job_description: str, api_key: str) -> dict:
    candidates = []

    for idx, (name, text) in enumerate(resumes.items(), 1):
        candidates.append({
            "rank": idx,
            "name": name,
            "overall_score": 75,
            "match_level": "Good",
            "matched_skills": ["Python", "Problem Solving"],
            "missing_skills": ["AWS"],
            "experience_match": "Basic match",
            "education_match": "Meets requirements",
            "strengths": ["Well formatted resume"],
            "improvement_suggestions": ["Add projects", "Improve keywords"]
        })

    return {
        "ranked_candidates": candidates,
        "summary": "Demo analysis (AI disabled).",
        "top_recommendation": candidates[0]["name"] if candidates else ""
    }


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
#  MAIN CONTENT (RESTORED)
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>🎯 AI Resume Analyzer</h1>
  <p>Upload resumes · Get instant analysis</p>
</div>
""", unsafe_allow_html=True)

job_description = st.text_area(
    "📋 Job Description",
    height=200
)

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

        for cand in result["ranked_candidates"]:
            st.markdown(f"""
            <div class="card">
                <h3>{cand['rank']}️⃣ {cand['name']}</h3>
                <p><b>Score:</b> {cand['overall_score']}%</p>
                <p><b>Match:</b> {cand['match_level']}</p>
            </div>
            """, unsafe_allow_html=True)
