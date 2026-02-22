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

# Courses aur Skills ka detailed mapping
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
    "https://www.youtube.com/watch?v=y8Yv4pnO7QC",  # Resume Optimization
    "https://www.youtube.com/watch?v=HG68Ymazo18",  # Technical Interview Prep
    "https://www.youtube.com/watch?v=JzPfNhVv-G8"   # Cracking the ATS
]

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="SkillSync AI Pro",
    page_icon="None",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS (PREMIUM DARK THEME) ----------------

st.markdown("""
<style>
    /* Main Background aur Font Styles */
    .main { background-color: #0e1117; }
    body { color: #e0e0e0; font-family: 'Inter', sans-serif; }
    
    /* Branding Header - No Emojis */
    .main-header {
        text-align: center;
        font-size: 4.5rem;
        font-weight: 900;
        background: -webkit-linear-gradient(#6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -50px;
        margin-bottom: 5px;
    }
    .sub-header {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.2rem;
        letter-spacing: 2px;
        margin-bottom: 50px;
        text-transform: uppercase;
    }

    /* Cards aur Containers */
    .stApp { background-color: #0e1117; }
    .css-1r6slb0 { background-color: #161b22; border-radius: 15px; padding: 20px; }
    
    .card {
        background: #1c2128;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }
    
    /* Skill Tags Styles */
    .tag {
        padding: 8px 18px;
        border-radius: 50px;
        display: inline-block;
        margin: 5px;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .tag-matched { background-color: rgba(35, 134, 54, 0.2); color: #3fb950; border: 1px solid #238636; }
    .tag-missing { background-color: rgba(248, 81, 73, 0.2); color: #f85149; border: 1px solid #da3633; }

    /* Button Customization */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 15px;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(37, 117, 252, 0.4);
    }
    
    /* Metrics aur Indicators */
    [data-testid="stMetricValue"] { font-size: 2rem !important; color: #2575fc !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR NAVIGATION ----------------

st.sidebar.markdown("<h2 style='text-align: center; color: white;'>SkillSync Menu</h2>", unsafe_allow_html=True)
navigation = st.sidebar.radio("Go To Section:", ["Analysis Dashboard", "Admin Insights", "System Architecture"])

# ---------------- HELPER FUNCTIONS ----------------

def generate_report_pdf(score, matched, missing, domain, health):
    """Resume analysis ki detailed PDF report generate karta hai."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom Title Style
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=24, spaceAfter=20)
        
        content = []
        content.append(Paragraph("SkillSync Pro Analysis Report", title_style))
        content.append(Spacer(1, 0.2 * inch))
        
        # Performance Summary Table
        data = [
            ["Metric", "Value"],
            ["Overall Match Score", f"{score}%"],
            ["Predicted Domain", domain],
            ["Structural Health", f"{health}/4"]
        ]
        t = Table(data, colWidths=[2 * inch, 2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        content.append(t)
        content.append(Spacer(1, 0.4 * inch))
        
        # Matched Skills Section
        content.append(Paragraph("Identified Technical Strengths:", styles['Heading2']))
        matched_items = [ListItem(Paragraph(s, styles['Normal'])) for s in matched]
        content.append(ListFlowable(matched_items, bulletType='bullet'))
        
        doc.build(content)
        return tmp.name

# ---------------- MAIN APP LOGIC ----------------

if navigation == "Analysis Dashboard":
    st.markdown('<p class="main-header">SkillSync AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Professional ATS Simulation and Career Intelligence</p>', unsafe_allow_html=True)

    # Input Section Container
    with st.container():
        c1, c2 = st.columns([1, 1], gap="large")
        
        with c1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Document Upload")
            uploaded_file = st.file_uploader("Choose Resume File (PDF or DOCX)", type=["pdf", "docx"])
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Job Specification")
            jd_text = st.text_area("Paste the Job Description Content Here", height=180, placeholder="Required skills: Python, Cloud Computing...")
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("EXECUTE DEEP ANALYSIS"):
        if uploaded_file and jd_text:
            with st.spinner("Processing vectors and extracting entities..."):
                # File Extraction logic
                if uploaded_file.name.endswith(".pdf"):
                    raw_text = extract_text_from_pdf(uploaded_file)
                else:
                    raw_text = extract_text_from_docx(uploaded_file)
                
                # Match Engine call
                score, matched, missing = calculate_match_score(raw_text, jd_text)
                
                # Domain Prediction Logic
                predicted_domain = "General Technology"
                for domain, d_data in TECH_STACK_DATA.items():
                    if any(kw in raw_text.lower() for kw in d_data["keywords"]):
                        predicted_domain = domain
                        break
                
                # Structural Analysis (Section checking)
                checks = {
                    "Objective": "objective" in raw_text.lower() or "summary" in raw_text.lower(),
                    "Education": "education" in raw_text.lower(),
                    "Projects": "projects" in raw_text.lower(),
                    "Experience": "experience" in raw_text.lower()
                }
                health_score = sum(checks.values())

            st.markdown("---")
            
            # Key Performance Indicators
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("ATS Match", f"{score}%")
            k2.metric("Health", f"{health_score}/4")
            k3.metric("Domain", predicted_domain)
            k4.metric("Gaps Found", len(missing))

            # Visualizations Row
            v1, v2 = st.columns([1.2, 1], gap="medium")
            
            with v1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': "Compatibility Index", 'font': {'size': 24, 'color': "white"}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': "white"},
                        'bar': {'color': "#2575fc"},
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(248, 81, 73, 0.1)"},
                            {'range': [50, 75], 'color': "rgba(255, 166, 0, 0.1)"},
                            {'range': [75, 100], 'color': "rgba(63, 185, 80, 0.1)"}
                        ],
                        'threshold': {'line': {'color': "white", 'width': 4}, 'value': score}
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=450)
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with v2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### Skill Distribution")
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=[len(matched), len(missing), score/10, health_score * 2, 8],
                    theta=["Strength", "Gaps", "Semantic", "Structure", "Clarity"],
                    fill='toself', line_color='#2575fc'
                ))
                fig_radar.update_layout(
                    polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 10])),
                    paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=400
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Skill Breakdown Columns
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns(2, gap="large")
            
            with b1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### Matched Proficiencies")
                if matched:
                    for s in matched: st.markdown(f"<span class='tag tag-matched'>{s}</span>", unsafe_allow_html=True)
                else: st.write("No technical matches found.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with b2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### Requirement Gaps")
                if missing:
                    for s in missing: st.markdown(f"<span class='tag tag-missing'>{s}</span>", unsafe_allow_html=True)
                else: st.success("Document fully satisfies all requirements.")
                st.markdown("</div>", unsafe_allow_html=True)

            # Improvement Logic aur Recommendations
            st.markdown("---")
            st.markdown("## Strategic Recommendations")
            
            r1, r2 = st.columns([1, 1.5], gap="large")
            
            with r1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### Resume Health Check")
                for item, status in checks.items():
                    color = "#3fb950" if status else "#f85149"
                    label = "Present" if status else "Missing"
                    st.markdown(f"<p style='color:{color}; font-weight:bold;'>{item}: {label}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # PDF Download Button
                report_path = generate_report_pdf(score, matched, missing, predicted_domain, health_score)
                with open(report_path, "rb") as f:
                    st.download_button("DOWNLOAD FULL PDF REPORT", f, file_name=f"SkillSync_Report_{score}.pdf")

            with r2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"### Targeted Learning Path: {predicted_domain}")
                suggested_courses = TECH_STACK_DATA.get(predicted_domain, TECH_STACK_DATA["Web Development"])["courses"]
                for c_name, c_url in suggested_courses:
                    st.markdown(f"- **{c_name}**: [Enroll Here]({c_url})")
                
                st.markdown("### Interview Preparation Video")
                st.video(random.choice(VIDEO_GUIDES))
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.error("Error: Please provide both the Resume file and Job Description to proceed.")

elif navigation == "Admin Insights":
    st.markdown("## Global Usage Analytics")
    
    # Mock Data for Visualization
    admin_data = {
        "Timestamp": [datetime.datetime.now() - datetime.timedelta(days=i) for i in range(10)],
        "Users": [random.randint(10, 50) for _ in range(10)],
        "AvgScore": [random.randint(40, 85) for _ in range(10)]
    }
    df_admin = pd.DataFrame(admin_data)
    
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        fig_users = px.line(df_admin, x="Timestamp", y="Users", title="Daily Active Users", template="plotly_dark")
        st.plotly_chart(fig_users, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with a2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        fig_score = px.bar(df_admin, x="Timestamp", y="AvgScore", title="Average Match Success Rate", template="plotly_dark")
        st.plotly_chart(fig_score, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Recent System Activity")
    mock_logs = pd.DataFrame({
        "User ID": [f"USR_{random.randint(1000, 9999)}" for _ in range(5)],
        "Domain": ["Data Science", "Web Dev", "DevOps", "Data Science", "Marketing"],
        "Final Score": [78, 45, 92, 64, 30],
        "Status": ["Elite", "Average", "Elite", "Good", "Critical"]
    })
    st.table(mock_logs)

elif navigation == "System Architecture":
    st.markdown("## Technical Architecture")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("""
    SkillSync AI utilizes a hybrid processing pipeline:
    1.  **Extraction Layer**: PyMuPDF and Python-Docx are used for high-fidelity text recovery.
    2.  **Entity Intelligence**: spaCy NER (Named Entity Recognition) with custom EntityRulers identifies technical proficiencies.
    3.  **Semantic Engine**: Sentence-BERT (SBERT) generates contextual embeddings to measure similarity beyond simple keyword matching.
    4.  **Heuristic Scorer**: A weighted proximity-based algorithm calculates the final compatibility score.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer credits
st.markdown("<p style='text-align: center; color: #444;'>SkillSync AI Enterprise Solution | Developed for High-Performance Recruitment</p>", unsafe_allow_html=True)

# Job Description : We are looking for professionals who are efficient with c++, machine learning, sql and python. It's good to have skills like java but docker is a mandatory skill.