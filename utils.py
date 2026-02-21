import fitz
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------
# TEXT EXTRACTION
# -----------------------------

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


# -----------------------------
# TEXT CLEANING
# -----------------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text


# -----------------------------
# MATCHING + HYBRID ATS SCORE
# -----------------------------

def calculate_match_score(resume_text, jd_text):

    skills = [
        "python", "java", "c++",
        "machine learning", "deep learning",
        "react", "node", "mongodb",
        "sql", "aws", "docker", "git"
    ]

    matched = []
    missing = []

    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())

    # ---- Skill Matching (Multi-word safe) ----
    for skill in skills:
        skill_words = skill.split()

        # If skill appears in job description
        if all(word in jd_words for word in skill_words):

            # If skill appears in resume
            if all(word in resume_words for word in skill_words):
                matched.append(skill)
            else:
                missing.append(skill)

    total_skills = len(matched) + len(missing)

    skill_score = (
        int((len(matched) / total_skills) * 100)
        if total_skills != 0 else 0
    )

    # ---- Semantic Similarity (TF-IDF) ----
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    semantic_score = int(similarity * 100)

    # ---- Hybrid Final Score ----
    final_score = int((skill_score * 0.6) + (semantic_score * 0.4))

    return final_score, matched, missing