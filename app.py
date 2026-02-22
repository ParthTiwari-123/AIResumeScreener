import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import datetime
import random
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
import spacy
from spacy.cli import download

try:
    nlp = spacy.load("en_core_web_sm")
except:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

from updated_utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    calculate_match_score,
    clean_text
)

# ---------------- CONFIGURATION AUR DATA ----------------

TECH_STACK_DATA = {
    "Data Science": {
        "courses": [
            ("Advanced Machine Learning Specialization", "https://coursera.org"),
            ("Deep Learning with PyTorch", "https://udemy.com"),
            ("Data Engineering Nanodegree", "https://udacity.com")
        ],
        "keywords": ["machine learning", "python", "sql", "tensorflow", "pytorch", "nlp"]
    },
    "Web Development": {
        "courses": [
            ("Full Stack React Masterclass", "https://udemy.com"),
            ("Node.js Backend Development", "https://frontendmasters.com"),
            ("System Design for Web Scalability", "https://educative.io")
        ],
        "keywords": ["react", "javascript", "node", "html", "css", "mongodb", "aws"]
    },
    "DevOps & Cloud": {
        "courses": [
            ("Docker and Kubernetes: The Complete Guide", "https://udemy.com"),
            ("AWS Certified Solutions Architect", "https://acloudguru.com"),
            ("Terraform Infrastructure as Code", "https://hashicorp.com")
        ],
        "keywords": ["docker", "kubernetes", "aws", "jenkins", "terraform", "linux"]
    }
}

VIDEO_GUIDES = [
    "https://www.youtube.com/watch?v=y8Yv4pnO7QC",
    "https://www.youtube.com/watch?v=HG68Ymazo18",
    "https://www.youtube.com/watch?v=JzPfNhVv-G8"
]

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="SkillSync AI Pro",
    layout="wide"
)

# ---------------- CUSTOM CSS (PREMIUM LIGHT THEME) ----------------

st.markdown("""
<style>

/* Import Premium Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* Global */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Remove default padding blocks */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Remove unwanted white boxes */
div[data-testid="stVerticalBlock"] > div:empty {
    display: none !important;
}

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: #f8fafc;
}

/* Header */
.main-header {
    text-align: center;
    font-size: 4.5rem;
    font-weight: 900;
    background: linear-gradient(90deg,#6366f1,#a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeDown 1s ease forwards;
}

.sub-header {
    text-align: center;
    color: #9ca3af;
    font-size: 1.2rem;
    margin-bottom: 3rem;
    animation: fadeUp 1.2s ease forwards;
}

/* Card Style */
.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s ease;
    animation: fadeUp 0.8s ease forwards;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

/* Inputs */
textarea, .stFileUploader {
    border-radius: 15px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    background: rgba(255,255,255,0.04) !important;
    color: white !important;
    transition: 0.3s;
}

textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.3);
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg,#6366f1,#a855f7);
    border: none;
    border-radius: 14px;
    padding: 14px;
    font-weight: 700;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    color: white;
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 30px rgba(139,92,246,0.4);
}

/* Metric Style */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    transition: 0.3s;
}

[data-testid="stMetric"]:hover {
    transform: scale(1.05);
}

/* Tags */
.tag {
    padding: 8px 16px;
    border-radius: 30px;
    display: inline-block;
    margin: 6px;
    font-size: 13px;
    font-weight: 600;
    animation: fadeUp 0.5s ease forwards;
}

.tag-matched {
    background: rgba(16,185,129,0.2);
    color: #10b981;
    border: 1px solid #10b981;
}

.tag-missing {
    background: rgba(239,68,68,0.2);
    color: #ef4444;
    border: 1px solid #ef4444;
}

/* Animations */
@keyframes fadeUp {
    from { opacity:0; transform: translateY(20px); }
    to { opacity:1; transform: translateY(0); }
}

@keyframes fadeDown {
    from { opacity:0; transform: translateY(-20px); }
    to { opacity:1; transform: translateY(0); }
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 4rem;
    color: #6b7280;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ----------------

def generate_report_pdf(score, matched, missing, domain, health):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=26, spaceAfter=30)
        
        content = []
        content.append(Paragraph("SkillSync Pro Analysis Report", title_style))
        content.append(Spacer(1, 0.3 * inch))
        
        data = [
            ["Metric", "Value"],
            ["Overall Match Score", f"{score}%"],
            ["Predicted Domain", domain],
            ["Structural Health", f"{health}/4"]
        ]
        t = Table(data, colWidths=[2.5 * inch, 2.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        content.append(t)
        content.append(Spacer(1, 0.5 * inch))
        
        content.append(Paragraph("Key Technical Assets Identified:", styles['Heading2']))
        matched_items = [ListItem(Paragraph(s, styles['Normal'])) for s in matched]
        content.append(ListFlowable(matched_items, bulletType='bullet'))
        
        doc.build(content)
        return tmp.name

# ---------------- MAIN UI ----------------

st.markdown('<div class="main-header">SkillSync AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent ATS Resume Intelligence Engine</div>', unsafe_allow_html=True)
# Main Container

c1, c2 = st.columns([1, 1], gap="large")
    
with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Resume Upload")
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Job Description")
        jd_text = st.text_area("Paste requirement details", height=150, placeholder="Describe the ideal candidate...", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("RUN ANALYSIS")
if run:
    if uploaded_file and jd_text:
        with st.spinner("Extracting semantic markers..."):
            if uploaded_file.name.endswith(".pdf"):
                raw_text = extract_text_from_pdf(uploaded_file)
            else:
                raw_text = extract_text_from_docx(uploaded_file)
            
            score, matched, missing = calculate_match_score(raw_text, jd_text)
            
            predicted_domain = "General Technology"
            for domain, d_data in TECH_STACK_DATA.items():
                if any(kw in raw_text.lower() for kw in d_data["keywords"]):
                    predicted_domain = domain
                    break
            
            checks = {
                "Professional Summary": "objective" in raw_text.lower() or "summary" in raw_text.lower(),
                "Academic History": "education" in raw_text.lower(),
                "Project Portfolio": "projects" in raw_text.lower(),
                "Work Experience": "experience" in raw_text.lower()
            }
            health_score = sum(checks.values())
        
        st.markdown("<hr style='margin-top:40px; margin-bottom:40px; border:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
        
        # Dashboard Overview
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("ATS Match", f"{score}%")
        k2.metric("Structure", f"{health_score}/4")
        k3.metric("Predicted Domain", predicted_domain)
        k4.metric("Gaps Found", len(missing))

        # Charts Section
        v1, v2 = st.columns([1.2, 1], gap="large")
        
        with v1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': "#6f7681"},
                    'bar': {'color': "#5e57e5"},
                    'bgcolor': "#ffffff",
                    'steps': [
                        {'range': [0, 50], 'color': "#fec6c6"},
                        {'range': [50, 75], 'color': "#fbecb1"},
                        {'range': [75, 100], 'color': "#b0ffd6"}
                    ],
                }
            ))
            fig_gauge.update_layout(title={'text': "Match Confidence", 'x': 0.5}, font={'color': "#ADB6CA"}, height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with v2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[len(matched), len(missing), score/10, health_score * 2, 8],
                theta=["Strengths", "Gaps", "Semantic Fit", "Structure", "Clarity"],
                fill='toself', line_color='#4f46e5'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                showlegend=False, height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Matched/Missing Row
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2, gap="large")
        
        with b1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Identified Proficiencies")
            if matched:
                for s in matched: st.markdown(f"<span class='tag tag-matched'>{s}</span>", unsafe_allow_html=True)
            else: st.write("No direct matches found.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with b2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Requirement Gaps")
            if missing:
                for s in missing: st.markdown(f"<span class='tag tag-missing'>{s}</span>", unsafe_allow_html=True)
            else: st.success("Document satisfies all technical requirements.")
            st.markdown("</div>", unsafe_allow_html=True)

        # Strategic Advisor
        st.markdown("---")
        st.markdown("## Career Strategic Roadmap")
        
        r1, r2 = st.columns([1, 1.5], gap="large")
        
        with r1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Structural Health")
            for item, status in checks.items():
                color = "#059669" if status else "#dc2626"
                label = "Verified" if status else "Missing"
                st.markdown(f"<p style='color:{color}; font-weight:bold; font-size: 1.1rem;'>{item}: {label}</p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            report_path = generate_report_pdf(score, matched, missing, predicted_domain, health_score)
            with open(report_path, "rb") as f:
                st.download_button("EXPORT PDF REPORT", f, file_name=f"SkillSync_Report.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with r2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"### Recommended Learning Path: {predicted_domain}")
            suggested_courses = TECH_STACK_DATA.get(predicted_domain, TECH_STACK_DATA["Web Development"])["courses"]
            for c_name, c_url in suggested_courses:
                st.markdown(f"- **{c_name}**: [Access Course]({c_url})")
            
            st.markdown("### Expert Video Tutorial")
            st.video(random.choice(VIDEO_GUIDES))
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Action Required: Please upload a resume and job description to start the engine.")

# Footer
st.markdown("<div class='footer'>Made with ♡</div>", unsafe_allow_html=True)

# Job Description : We are looking for professionals who are efficient with c++, machine learning, sql and python. It's good to have skills like java but docker is a mandatory skill.