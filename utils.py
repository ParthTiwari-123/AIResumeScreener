import fitz
import docx
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- TEXT EXTRACTION --------

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

# -------- CLEAN TEXT --------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# -------- IMPORTANCE --------

IMPORTANCE_LEVELS = {
    3: ["must", "mandatory", "required", "heavy demand"],
    2: ["preferred", "should have"],
    1: ["nice to have"]
}

# -------- DYNAMIC SKILLS --------

def extract_dynamic_skills(jd_text):
    words = jd_text.split()
    word_freq = Counter(words)

    min_freq = 1 if len(words) < 50 else 2

    stopwords = {
        "the", "and", "with", "for", "in", "of", "to", "is",
        "a", "an", "on", "at", "by", "from",
        "experience", "looking", "candidate",
        "role", "ability", "team", "work",
        "skills", "knowledge", "we", "are"
    }

    skills = set()

    for word in words:
        if word not in stopwords and len(word) >= 3 and word_freq[word] >= min_freq:
            skills.add(word)

    bigrams = [words[i] + " " + words[i + 1] for i in range(len(words) - 1)]
    bigram_freq = Counter(bigrams)

    for bg in bigrams:
        w1, w2 = bg.split()
        if w1 not in stopwords and w2 not in stopwords and bigram_freq[bg] >= min_freq:
            skills.add(bg)

    return list(skills)

# -------- MATCH SCORE --------

def calculate_match_score(resume_text, jd_text):

    skills = extract_dynamic_skills(jd_text)

    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    matched = []
    missing = []

    total_weight = 0
    matched_weight = 0

    for skill in skills:

        weight = 2

        for level, keywords in IMPORTANCE_LEVELS.items():
            for keyword in keywords:
                pattern = rf"{keyword}(.{{0,40}}){skill}|{skill}(.{{0,40}}){keyword}"
                if re.search(pattern, jd_lower):
                    weight = level

        total_weight += weight

        if skill in resume_lower:
            matched.append(skill)
            matched_weight += weight
        else:
            missing.append(skill)

    skill_score = int((matched_weight / total_weight) * 100) if total_weight != 0 else 0

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    semantic_score = int(similarity * 100)

    final_score = int((skill_score * 0.6) + (semantic_score * 0.4))

    return final_score, matched, missing