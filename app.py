import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx

st.set_page_config(page_title="AI Resume Screener")

st.title("📄 AI Resume Screener (ATS Simulator)")

uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
job_description = st.text_area("Paste Job Description Here")

if uploaded_file and job_description:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    st.subheader("📌 Extracted Resume Text")
    st.write(resume_text[:1000])  # show first 1000 chars

    st.subheader("📌 Job Description")
    st.write(job_description)
