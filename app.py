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

# Updated utils se functions import kar rahe hain
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
    /* Main Background aur Font Styles */
    .main { background-color: #ffffff; }
    body { color: #1f2937; font-family: 'Inter', sans-serif; }
    
    /* Branding Header - Large & Centered */
    .main-header {
        text-align: center;
        font-size: 6rem;
        font-weight: 900;
        background: -webkit-linear-gradient(#4f46e5, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        margin-bottom: 0px;
        letter-spacing: -2px;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.5rem;
        font-weight: 400;
        margin-bottom: 60px;
    }

    /* Cards aur Containers */
    .card {
        background: #f9fafb;
        padding: 40px;
        border-radius: 24px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    
    /* Skill Tags Styles */
    .tag {
        padding: 10px 20px;
        border-radius: 12px;
        display: inline-block;
        margin: 6px;
        font-size: 14px;
        font-weight: 600;
    }
    .tag-matched { background-color: #d1fae5; color: #065f46; border: 1px solid #10b981; }
    .tag-missing { background-color: #fee2e2; color: #991b1b; border: 1px solid #f87171; }

    /* Button Customization */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #9333ea 100%);
        color: white;
        border: none;
        padding: 20px;
        border-radius: 16px;
        font-size: 1.25rem;
        font-weight: 800;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; color: #4f46e5 !important; font-weight: 800 !important; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 50px 0;
        color: #9ca3af;
        font-size: 1.1rem;
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

st.markdown('<p class="main-header">SkillSync</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent Professional ATS Simulation</p>', unsafe_allow_html=True)

# Main Container
with st.container():
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📄 Resume Upload")
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📝 Job Description")
        jd_text = st.text_area("Paste requirement details", height=150, placeholder="Describe the ideal candidate...", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

if st.button("RUN ANALYSIS"):
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

        st.markdown("---")
        
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
                    'axis': {'range': [0, 100], 'tickcolor': "#4b5563"},
                    'bar': {'color': "#4f46e5"},
                    'bgcolor': "#ffffff",
                    'steps': [
                        {'range': [0, 50], 'color': "#fee2e2"},
                        {'range': [50, 75], 'color': "#fef3c7"},
                        {'range': [75, 100], 'color': "#d1fae5"}
                    ],
                }
            ))
            fig_gauge.update_layout(title={'text': "Match Confidence", 'x': 0.5}, font={'color': "#111827"}, height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with v2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center;'>Skill Distribution</h4>", unsafe_allow_html=True)
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
            st.markdown("### ✅ Identified Proficiencies")
            if matched:
                for s in matched: st.markdown(f"<span class='tag tag-matched'>{s}</span>", unsafe_allow_html=True)
            else: st.write("No direct matches found.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with b2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### ❌ Requirement Gaps")
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