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


# ✅ DUMMY ANALYSIS (REPLACED GROQ ONLY)
def analyze_resumes_with_groq(resumes: dict, job_description: str, api_key: str) -> dict:
    candidates = []

    for idx, (name, text) in enumerate(resumes.items(), 1):
        candidates.append({
            "rank": idx,
            "name": name,
            "overall_score": 70,
            "match_level": "Good",
            "matched_skills": ["Python", "Problem Solving"],
            "missing_skills": ["AWS", "Docker"],
            "experience_match": "Basic match",
            "education_match": "Meets requirements",
            "strengths": ["Clean resume", "Relevant keywords"],
            "improvement_suggestions": [
                "Add more projects",
                "Use strong action verbs",
                "Include measurable achievements"
            ]
        })

    return {
        "ranked_candidates": candidates,
        "summary": "Demo analysis (AI disabled).",
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
#  MAIN CONTENT
# ─────────────────────────────────────────────
st.title("🎯 AI Resume Analyzer")

job_description = st.text_area(
    "📋 Job Description",
    height=200
)

# ✅ FIXED BUTTON (IMPORTANT)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("🚀 Analyze Resumes with AI", use_container_width=True)


# ─────────────────────────────────────────────
#  ANALYSIS
# ─────────────────────────────────────────────
if analyze_btn:
    errors = []

    if not uploaded_files or not (3 <= len(uploaded_files) <= 5):
        errors.append("❌ Please upload between 3 and 5 PDF resumes.")
    if not job_description.strip():
        errors.append("❌ Please enter a job description.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("📄 Reading PDF resumes..."):
            resumes = {}
            progress = st.progress(0)
            for i, f in enumerate(uploaded_files):
                f.seek(0)
                text = extract_text_from_pdf(f)
                resumes[f.name] = text if text else f"[Could not extract text from {f.name}]"
                progress.progress((i + 1) / len(uploaded_files))
            time.sleep(0.3)
            progress.empty()

        with st.spinner("⚡Analyzing resumes (Demo mode)..."):
            result = analyze_resumes_with_groq(resumes, job_description, api_key)

        st.success("✅ Analysis complete!")

        candidates = result.get("ranked_candidates", [])

        for cand in candidates:
            st.subheader(f"{cand['rank']}️⃣ {cand['name']}")
            st.write(f"Score: {cand['overall_score']}%")
            st.write(f"Match: {cand['match_level']}")

            st.write("✅ Matched Skills:", cand["matched_skills"])
            st.write("❌ Missing Skills:", cand["missing_skills"])

            st.write("💪 Strengths:")
            for s in cand["strengths"]:
                st.write("-", s)

            st.write("💡 Improvements:")
            for s in cand["improvement_suggestions"]:
                st.write("-", s)

            st.markdown("---")
