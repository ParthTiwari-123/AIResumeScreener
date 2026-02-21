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

# ---------------- LIGHT/DARK MODE ----------------
mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if mode:
    bg_color = "#0e1117"
    card_color = "rgba(255,255,255,0.08)"
else:
    bg_color = "#f4f6f9"
    card_color = "rgba(255,255,255,0.7)"

# ---------------- GLASS STYLE ----------------
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
}}
.main {{
    background-color: {bg_color};
}}
.glass {{
    background: {card_color};
    backdrop-filter: blur(14px);
    padding: 30px;
    border-radius: 18px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
    margin-top: 25px;
}}
.skill-tag {{
    padding: 6px 12px;
    border-radius: 20px;
    display: inline-block;
    margin: 4px;
    font-size: 13px;
}}
.matched {{
    background: #00c9a7;
    color: black;
}}
.missing {{
    background: #ff4b5c;
    color: white;
}}
.stButton>button {{
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-weight: 600;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🚀 AI Resume Screener")
st.markdown("### Intelligent ATS Simulator Dashboard")

# ---------------- INPUT SECTION ----------------
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf", "docx"])

with col2:
    job_description = st.text_area("📝 Paste Job Description", height=200)

# ---------------- ANALYZE BUTTON ----------------
if st.button("Analyze Resume 🔍"):

    if uploaded_file and job_description:

        with st.spinner("⚡ Analyzing Resume with AI..."):

            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = extract_text_from_docx(uploaded_file)

            resume_text = clean_text(resume_text)
            jd_text = clean_text(job_description)

            score, matched, missing = calculate_match_score(resume_text, jd_text)

        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        # -------- CIRCULAR GAUGE --------
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
        st.plotly_chart(gauge, width="stretch")

        # -------- RADAR CHART --------
        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=[len(matched), len(missing), score],
            theta=["Matched Skills", "Missing Skills", "Overall Score"],
            fill='toself'
        ))
        radar.update_layout(showlegend=False)
        st.subheader("🧠 Skill Radar Analysis")
        st.plotly_chart(radar, width="stretch")

        # -------- BREAKDOWN BAR --------
        breakdown = px.bar(
            x=["Matched Skills", "Missing Skills"],
            y=[len(matched), len(missing)],
            labels={'x': 'Category', 'y': 'Count'}
        )
        st.subheader("📈 Skill Breakdown")
        st.plotly_chart(breakdown, width="stretch")

        # -------- SKILL TAGS --------
        col_match, col_missing = st.columns(2)

        with col_match:
            st.subheader("✅ Matched Skills")
            if matched:
                for skill in matched:
                    st.markdown(
                        f"<span class='skill-tag matched'>{skill}</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.write("No matching skills.")

        with col_missing:
            st.subheader("❌ Missing Skills")
            if missing:
                for skill in missing:
                    st.markdown(
                        f"<span class='skill-tag missing'>{skill}</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.write("No missing skills.")

        st.markdown("</div>", unsafe_allow_html=True)

        # -------- PDF REPORT --------
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
                    "🎯 Download PDF Report",
                    f,
                    file_name="ATS_Report.pdf"
                )

            os.unlink(tmpfile.name)

    else:
        st.warning("Please upload resume and paste job description.")