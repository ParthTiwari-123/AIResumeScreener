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

def extract_dynamic_skills(jd_text):

    stopwords = {
        "the", "and", "with", "for", "in", "of", "to", "is",
        "a", "an", "on", "at", "by", "from",
        "experience", "required", "looking", "candidate",
        "role", "strong", "good", "ability", "team", "work",
        "skills", "knowledge"
    }

    words = jd_text.split()

    skills = set()

    # 1-gram skills
    for word in words:
        if word not in stopwords and len(word) >= 3:
            skills.add(word)

    # 2-gram skills
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if w1 not in stopwords and w2 not in stopwords:
            skills.add(w1 + " " + w2)

    return list(skills)

def calculate_match_score(resume_text, jd_text):

    skills = extract_dynamic_skills(jd_text)

    matched = []
    missing = []

    resume_words = set(resume_text.split())

    for skill in skills:
        skill_words = skill.split()

        if all(word in resume_words for word in skill_words):
            matched.append(skill)
        else:
            missing.append(skill)

    total_skills = len(matched) + len(missing)

    skill_score = (
        int((len(matched) / total_skills) * 100)
        if total_skills != 0 else 0
    )

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    semantic_score = int(similarity * 100)

    final_score = int((skill_score * 0.6) + (semantic_score * 0.4))

    return final_score, matched, missing
