import streamlit as st
import pdfplumber
import json
import time
import re
from io import BytesIO
import os

# ─────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
)

load_css()  # ✅ APPLY CSS

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        st.warning(f"Error reading {uploaded_file.name}: {e}")
    return text.strip()

# ✅ DUMMY ANALYSIS (NO API)
def analyze_resumes(resumes, job_description):
    results = []
    for i, (name, _) in enumerate(resumes.items(), 1):
        results.append({
            "rank": i,
            "name": name,
            "score": 75,
            "match": "Good"
        })
    return results

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload 3–5 PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

# ─────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────
st.title("🎯 AI Resume Analyzer")

job_description = st.text_area("📋 Job Description", height=200)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    analyze_btn = st.button("🚀 Analyze Resumes", use_container_width=True)

# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────
if analyze_btn:
    if not uploaded_files or not (3 <= len(uploaded_files) <= 5):
        st.error("Upload 3–5 resumes")
    elif not job_description.strip():
        st.error("Enter job description")
    else:
        resumes = {}
        for f in uploaded_files:
            resumes[f.name] = extract_text_from_pdf(f)

        results = analyze_resumes(resumes, job_description)

        st.success("✅ Analysis Complete!")

        for r in results:
            st.markdown(f"""
            <div class="card">
                <h3>{r['rank']}️⃣ {r['name']}</h3>
                <p>Score: {r['score']}%</p>
                <p>Match: {r['match']}</p>
            </div>
            """, unsafe_allow_html=True)
