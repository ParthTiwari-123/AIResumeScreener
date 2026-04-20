# SkillSyncAI Pro — AI-Powered Resume Analyzer

SkillSyncAI Pro is a hybrid AI-based ATS simulator that analyzes how well a resume aligns with a given job description.

It combines:
- Dynamic skill extraction from job descriptions
- Weighted importance scoring
- Semantic similarity using TF-IDF
- Hybrid scoring model

This project simulates how modern Applicant Tracking Systems (ATS) evaluate resume-job alignment.

---

## 🚀 Features

- 📄 Upload Resume (PDF / DOCX)
- 🧠 Dynamic Skill Extraction from Job Description
- ⚖️ Importance-based Skill Weighting
- 📊 Hybrid ATS Score (Skill + Semantic)
- 🔍 Matched & Missing Skill Breakdown
- 🖥️ Clean Streamlit UI

---

## 🧠 How It Works

### 1. Text Extraction
- PDF parsing using PyMuPDF (fitz)
- DOCX parsing using python-docx

### 2. Text Cleaning
- Lowercasing
- Special character removal

### 3. Dynamic Skill Extraction
- Generates 1-gram and 2-gram candidates from JD
- Removes stopwords
- Applies frequency filtering
- Produces dynamic skill list

### 4. Importance Weighting
Skills are weighted based on keywords found in the JD:

- Level 3 → must, mandatory, required
- Level 2 → preferred, should have
- Level 1 → nice to have

### 5. Hybrid Scoring Model

Final Score =  
60% Weighted Skill Match  
40% Semantic Similarity (TF-IDF + Cosine Similarity)

---

## 📊 Scoring Logic

Skill Score:
(matched_weight / total_weight) * 100

Semantic Score:
TF-IDF Vectorization → Cosine Similarity


Final Score:
(0.6 × Skill Score) + (0.4 × Semantic Score)


---

## 🛠️ Tech Stack

- Python
- Streamlit
- scikit-learn
- PyMuPDF
- python-docx
- NLP (TF-IDF, cosine similarity)

---

## 🎯 Future Improvements

- Advanced NLP-based skill extraction (NER)
- Resume section-wise scoring
- AI-based resume improvement suggestions
- Downloadable PDF analysis report
- Embedding-based semantic similarity
- Skill visualization dashboard

## 📌 Author

Built as part of an AI-driven resume intelligence system.


