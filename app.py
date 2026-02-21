import streamlit as st
from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    calculate_match_score
)

st.set_page_config(page_title="AI Resume Screener", layout="centered")

st.title("📄 AI Resume Screener (ATS Simulator)")
st.write("Upload your resume and paste the job description below.")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF/DOCX)",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste Job Description Here",
    height=200
)

if st.button("Analyze Resume"):

    if uploaded_file and job_description:

        # Extract Resume Text
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)

        # Clean Text
        resume_text = clean_text(resume_text)
        jd_text = clean_text(job_description)

        # Calculate Score
        score, matched, missing = calculate_match_score(resume_text, jd_text)

        st.divider()

        st.subheader("📊 ATS Match Score")
        st.metric("Overall Score", f"{score}%")
        st.progress(score)

        # Feedback
        if score < 50:
            st.error("Resume needs significant improvement.")
        elif score < 75:
            st.warning("Good match, but can improve further.")
        else:
            st.success("Excellent match! Strong alignment with job description.")
            st.balloons()

        st.divider()

        st.subheader("✅ Matched Skills")
        if matched:
            st.write(", ".join(matched))
        else:
            st.write("No matching skills found.")

        st.subheader("❌ Missing Skills")
        if missing:
            st.write(", ".join(missing))
        else:
            st.write("No major skills missing.")

    else:
        st.warning("Please upload resume and paste job description.")