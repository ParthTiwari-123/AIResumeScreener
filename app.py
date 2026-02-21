import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx
from utils import clean_text, calculate_match_score

st.set_page_config(page_title="AI Resume Screener")

st.title("📄 AI Resume Screener (ATS Simulator)")

uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
job_description = st.text_area("Paste Job Description Here")

if st.button("Analyze Resume"):
    if uploaded_file and job_description:

        # Extract Resume Text
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)

        # Clean Text
        resume_text = clean_text(resume_text)
        job_description = clean_text(job_description)

        # Calculate Match Score
        score, matched, missing = calculate_match_score(resume_text, job_description)

        st.subheader("📊 Match Score")
        st.success(f"{score}% Match")

        st.subheader("✅ Matched Skills")
        st.write(matched)

        st.subheader("❌ Missing Skills")
        st.write(missing)

    else:
        st.warning("Please upload resume and paste job description.")
