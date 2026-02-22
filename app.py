import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import tempfile
import os

from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    calculate_match_score
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Resume Screener", page_icon="🚀", layout="wide")

# ---------------- MODERN PROFESSIONAL STYLING ----------------
st.markdown("""
<style>
body {
    background: #f7f8fc;
}

.main {
    padding: 20px;
}

.card {
    background: white;
    padding: 26px;
    border-radius: 16px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
    transition: all 0.25s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 50px rgba(0, 0, 0, 0.12);
}

.skill-tag {
    padding: 6px 14px;
    border-radius: 18px;
    display: inline-block;
    margin: 4px;
    font-size: 13px;
    transition: transform 0.2s ease;
}

.skill-tag:hover {
    transform: scale(1.05);
}

.matched {
    background: #00c9a7;
    color: #ffffff;
}

.missing {
    background: #ff4b5c;
    color: #ffffff;
}

.stButton > button {
    width: 100%;
    height: 52px;
    border-radius: 14px;
    font-weight: 600;
    background: linear-gradient(135deg, #5b8def, #8e44fd);
    color: white;
    border: none;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(91, 141, 239, 0.35);
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("AI Resume Screener")
st.markdown("### Professional ATS Simulation & Skill Analysis")

# ---------------- INPUT SECTION ----------------
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

with col2:
    job_description = st.text_area("Paste Job Description", height=200)

# ---------------- ANALYZE BUTTON ----------------
if st.button("Analyze Resume"):

    if uploaded_file and job_description:

        with st.spinner("Analyzing resume..."):

            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = extract_text_from_docx(uploaded_file)

            resume_text = clean_text(resume_text)
            jd_text = clean_text(job_description)

            score, matched, missing = calculate_match_score(resume_text, jd_text)

        st.markdown("---")

        # RESULTS GRID
        col_g1, col_g2 = st.columns([1, 1])

        with col_g1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': "ATS Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#00c9a7"},
                    'steps': [
                        {'range': [0, 50], 'color': "#ff4b5c"},
                        {'range': [50, 75], 'color': "#ffa600"},
                        {'range': [75, 100], 'color': "#00c9a7"},
                    ],
                }
            ))
            st.plotly_chart(gauge, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_g2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            radar = go.Figure()
            radar.add_trace(go.Scatterpolar(
                r=[len(matched), len(missing), score],
                theta=["Matched Skills", "Missing Skills", "Overall Score"],
                fill='toself'
            ))
            radar.update_layout(showlegend=False)

            st.subheader("Skill Radar Analysis")
            st.plotly_chart(radar, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # BREAKDOWN
        st.markdown("---")
        col_b1, col_b2 = st.columns(2)

        with col_b1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            breakdown = px.bar(
                x=["Matched", "Missing"],
                y=[len(matched), len(missing)],
                labels={'x': 'Category', 'y': 'Count'}
            )
            st.subheader("Skill Breakdown")
            st.plotly_chart(breakdown, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.subheader("Matched Skills")
            if matched:
                for skill in matched:
                    st.markdown(
                        f"<span class='skill-tag matched'>{skill}</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.write("No matching skills.")

            st.subheader("Missing Skills")
            if missing:
                for skill in missing:
                    st.markdown(
                        f"<span class='skill-tag missing'>{skill}</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.write("No missing skills.")

            st.markdown("</div>", unsafe_allow_html=True)

        # PDF REPORT
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            doc = SimpleDocTemplate(tmpfile.name, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("AI Resume Screener Report", styles["Heading1"]))
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph(f"Overall Score: {score}%", styles["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

            elements.append(Paragraph("Matched Skills:", styles["Heading2"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(ListFlowable(
                [ListItem(Paragraph(skill, styles["Normal"])) for skill in matched]
            ))

            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph("Missing Skills:", styles["Heading2"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(ListFlowable(
                [ListItem(Paragraph(skill, styles["Normal"])) for skill in missing]
            ))

            doc.build(elements)

            with open(tmpfile.name, "rb") as f:
                st.download_button(
                    "Download PDF Report",
                    f,
                    file_name="ATS_Report.pdf"
                )

            os.unlink(tmpfile.name)

    else:
        st.warning("Please upload resume and paste job description.")