import fitz
import docx
import re

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

# Basic cleaning
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text


# Simple keyword-based scoring
def calculate_match_score(resume_text, jd_text):

    # Predefined skills list (can expand later)
    skills = [
        "python", "java", "c++", "machine learning",
        "deep learning", "react", "node", "mongodb",
        "sql", "aws", "docker", "git"
    ]

    matched = []
    missing = []

    for skill in skills:
        if skill in jd_text:
            if skill in resume_text:
                matched.append(skill)
            else:
                missing.append(skill)

    if len(matched) + len(missing) == 0:
        score = 0
    else:
        score = int((len(matched) / (len(matched) + len(missing))) * 100)

    return score, matched, missing
