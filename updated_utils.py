import fitz
import docx
import re
import nltk
from collections import Counter
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util

# Model load (Intelligence ke liye)
model = SentenceTransformer('all-MiniLM-L6-v2')

# NLTK Data Fix
try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

# -------- CONFIGURATIONS --------
IMPORTANCE_LEVELS = {
    3: ["must", "mandatory", "required", "need", "demand"],
    2: ["preferred", "should have", "efficient"],
    1: ["nice to have", "good to have", "like", "habitual"]
}

SKILL_ALIASES = {
    "machine learning": ["ml", "machine-learning"],
    "artificial intelligence": ["ai", "artificial-intelligence"],
    "javascript": ["js", "javascript"],
    "react": ["reactjs", "react.js", "react js"],
    "nodejs": ["node.js", "node js", "node"],
    "mongodb": ["mongo"],
    "aws": ["amazon web services"],
    "kubernetes": ["k8s"],
    "natural language processing": ["nlp"]
}

# -------- TEXT EXTRACTION --------
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
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# -------- SMART CLEANING --------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_aliases(text):
    for standard_name, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = rf'\b{re.escape(alias)}\b'
            text = re.sub(pattern, standard_name, text, flags=re.IGNORECASE)
    return text

# -------- DYNAMIC SKILL EXTRACTION (ULTRA-CLEAN) --------
def extract_dynamic_skills(jd_text):
    # Noise list expand kiya hai
    fluff = {
        "experience", "role", "work", "ability", "knowledge", "mandatory", 
        "habitual", "requirement", "skills", "professionals", "efficient",
        "good", "like", "need", "looking", "someone", "plus", "years", "professional"
    }
    stop_words = {
        "the", "and", "with", "for", "in", "of", "to", "is", "a", "an", "we", 
        "are", "have", "who", "but", "also", "from", "this", "that", "has", "have"
    }
    
    tokens = word_tokenize(jd_text.lower())
    tagged = nltk.pos_tag(tokens)
    
    skills = set()
    
    # 1-Gram: Strictly Nouns check
    for word, tag in tagged:
        if tag.startswith('NN') and word not in stop_words and word not in fluff and len(word) >= 2:
            skills.add(word)

    # 2-Gram: Technical phrases
    words = [w for w, t in tagged]
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        t1, t2 = tagged[i][1], tagged[i+1][1]
        
        if w1 not in stop_words and w2 not in stop_words and w1 not in fluff and w2 not in fluff:
            if t1.startswith('NN') or t2.startswith('NN'):
                skills.add(f"{w1} {w2}")
            
    return list(skills)

# -------- MATCH SCORE ENGINE --------
def calculate_match_score(resume_text, jd_text):
    resume_processed = normalize_aliases(clean_text(resume_text))
    jd_processed = normalize_aliases(clean_text(jd_text))

    skills = extract_dynamic_skills(jd_processed)

    matched = []
    missing = []
    total_weight = 0
    matched_weight = 0

    for skill in skills:
        weight = 2
        for level, keywords in IMPORTANCE_LEVELS.items():
            for keyword in keywords:
                pattern = rf"\b{re.escape(keyword)}\b(.{{0,40}})\b{re.escape(skill)}\b|\b{re.escape(skill)}\b(.{{0,40}})\b{re.escape(keyword)}\b"
                if re.search(pattern, jd_processed):
                    weight = level

        total_weight += weight
        
        if re.search(rf"\b{re.escape(skill)}\b", resume_processed):
            matched.append(skill)
            matched_weight += weight
        else:
            missing.append(skill)

    skill_score = int((matched_weight / total_weight) * 100) if total_weight != 0 else 0

    # SBERT Analysis (Context check)
    resume_embedding = model.encode(resume_processed, convert_to_tensor=True)
    jd_embedding = model.encode(jd_processed, convert_to_tensor=True)
    cosine_score = util.cos_sim(resume_embedding, jd_embedding)
    semantic_score = int(cosine_score.item() * 100)

    # Final Hybrid Score (60% Skill Match, 40% Semantic Context)
    final_score = int((skill_score * 0.6) + (semantic_score * 0.4))

    return final_score, matched, missing