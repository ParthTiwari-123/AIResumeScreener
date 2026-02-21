import streamlit as st
from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    calculate_match_score
)

st.set_page_config(page_title="AI Resume Screener", layout="centered")

st.title("AI Resume Screener")
st.caption("Analyze how well a resume aligns with a job description using hybrid ATS scoring.")

st.divider()

uploaded_file = st.file_uploader(
    "Upload Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=200
)

analyze = st.button("Analyze Resume", use_container_width=True)

if analyze:

    if uploaded_file and job_description:

        with st.spinner("Processing resume and analyzing match..."):

            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = extract_text_from_docx(uploaded_file)

            resume_text = clean_text(resume_text)
            jd_text = clean_text(job_description)

            score, matched, missing = calculate_match_score(resume_text, jd_text)

        st.divider()

        st.subheader("Match Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Overall Match Score", f"{score}%")
            st.progress(score)

        with col2:
            if score < 50:
                st.error("Low alignment with job description.")
            elif score < 75:
                st.warning("Moderate alignment. Improvement recommended.")
            else:
                st.success("Strong alignment with job description.")

        st.divider()

        st.subheader("Skill Breakdown")

        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:
            st.markdown("**Matched Skills**")
            if matched:
                for skill in matched:
                    st.write(f"- {skill}")
            else:
                st.write("No matching skills identified.")

        with skill_col2:
            st.markdown("**Missing Skills**")
            if missing:
                for skill in missing:
                    st.write(f"- {skill}")
            else:
                st.write("No major skill gaps detected.")

    else:
        st.warning("Please upload a resume and provide a job description.")
