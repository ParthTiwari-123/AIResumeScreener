import fitz
import docx
import re
import nltk
from sentence_transformers import SentenceTransformer, util

# Load semantic model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# NLTK setup
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# ---------------- CONFIG ----------------

IMPORTANCE_LEVELS = {
    3: ["must", "mandatory", "required", "need", "demand"],
    2: ["preferred", "should have", "strong"],
    1: ["nice to have", "good to have", "optional"]
}

SKILL_ALIASES = {
    "python": [],
    "sql": [],
    "machine learning": ["ml", "machine-learning"],
    "artificial intelligence": ["ai", "artificial-intelligence"],
    "javascript": ["js"],
    "react": ["reactjs", "react.js"],
    "nodejs": ["node.js"],
    "mongodb": ["mongo"],
    "aws": ["amazon web services"],
    "kubernetes": ["k8s"],
    "natural language processing": ["nlp"],
    "java": [],
    "c++": ["cpp"]
}

# ---------------- TEXT EXTRACTION ----------------

def extract_text_from_pdf(file):
    text = ""
    file.seek(0)
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    file.seek(0)
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# ---------------- CLEANING ----------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s\+]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def normalize_aliases(text):
    for standard, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            text = re.sub(rf'\b{re.escape(alias)}\b', standard, text)
    return text

# ---------------- SKILL EXTRACTION ----------------

def extract_dynamic_skills(jd_text):
    sentences = nltk.sent_tokenize(jd_text)
    skills = set()

    for sentence in sentences:
        for skill in SKILL_ALIASES.keys():
            if skill in sentence:
                skills.add(skill)

    return list(skills)

# ---------------- MATCH ENGINE ----------------

def calculate_match_score(resume_text, jd_text):

    resume_processed = normalize_aliases(clean_text(resume_text))
    jd_processed = normalize_aliases(clean_text(jd_text))

    skills = extract_dynamic_skills(jd_processed)

    matched = []
    missing = []

    total_weight = 0
    matched_weight = 0

    jd_sentences = nltk.sent_tokenize(jd_text.lower())

    for skill in skills:
        weight = 2  # default

        # Check importance ONLY in sentence containing skill
        for sentence in jd_sentences:
            if skill in sentence:
                for level, keywords in IMPORTANCE_LEVELS.items():
                    for keyword in keywords:
                        if keyword in sentence:
                            weight = level

        total_weight += weight

        if skill in resume_processed:
            matched.append(skill)
            matched_weight += weight
        else:
            missing.append(skill)

    skill_score = int((matched_weight / total_weight) * 100) if total_weight else 0

    # Semantic similarity
    resume_embedding = model.encode(resume_processed, convert_to_tensor=True)
    jd_embedding = model.encode(jd_processed, convert_to_tensor=True)

    semantic_score = int(util.cos_sim(resume_embedding, jd_embedding).item() * 100)

    # Final weighted score
    final_score = int((skill_score * 0.6) + (semantic_score * 0.4))

    return final_score, matched, missing