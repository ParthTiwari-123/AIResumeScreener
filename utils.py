import fitz
import docx
import re
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NLTK Data Download (Sirf ek baar handle karega)
try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('stopwords')
    nltk.download('punkt')

# -------- DATA DICTIONARIES --------

IMPORTANCE_LEVELS = {
    3: ["must", "mandatory", "required", "heavy demand"],
    2: ["preferred", "should have"],
    1: ["nice to have"]
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
    file.seek(0) # Pointer reset
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    file.seek(0) # Pointer reset
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# -------- CLEANING & NORMALIZATION --------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def normalize_aliases(text):
    for standard_name, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = rf'\b{re.escape(alias)}\b'
            text = re.sub(pattern, standard_name, text, flags=re.IGNORECASE)
    return text

# -------- DYNAMIC SKILL EXTRACTION (SMART VERSION) --------

def extract_dynamic_skills(jd_text):
    # Recruitment fluff words filter
    fluff = {"experience", "role", "work", "ability", "knowledge", "mandatory", "habitual", "requirement", "skills"}
    stop_words = {"the", "and", "with", "for", "in", "of", "to", "is", "a", "an", "we", "are", "have", "who"}
    
    # Tokenize and Tag parts of speech
    tokens = word_tokenize(jd_text.lower())
    tagged = nltk.pos_tag(tokens)
    
    skills = set()
    
    # 1-Gram: Only keep Nouns
    for word, tag in tagged:
        if tag.startswith('NN') and word not in stop_words and word not in fluff and len(word) >= 3:
            skills.add(word)

    # 2-Gram: Keep technical pairs
    words = [w for w, t in tagged]
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        t1, t2 = tagged[i][1], tagged[i+1][1]
        
        # Phrase cleaning
        if w1 not in stop_words and w2 not in stop_words and w1 not in fluff and w2 not in fluff:
            # At least one part should be a noun
            if t1.startswith('NN') or t2.startswith('NN'):
                skills.add(f"{w1} {w2}")
            
    return list(skills)

# -------- MATCH SCORE ENGINE --------

def calculate_match_score(resume_text, jd_text):
    # 1. Standardize Text
    resume_processed = normalize_aliases(clean_text(resume_text))
    jd_processed = normalize_aliases(clean_text(jd_text))

    # 2. Extract Smart Skills
    skills = extract_dynamic_skills(jd_processed)

    matched = []
    missing = []
    total_weight = 0
    matched_weight = 0

    # 3. Weighted Matching Logic
    for skill in skills:
        weight = 2
        for level, keywords in IMPORTANCE_LEVELS.items():
            for keyword in keywords:
                # Contextual weighting (Proximity match)
                pattern = rf"{keyword}(.{{0,40}}){re.escape(skill)}|{re.escape(skill)}(.{{0,40}}){keyword}"
                if re.search(pattern, jd_processed):
                    weight = level

        total_weight += weight

        if skill in resume_processed:
            matched.append(skill)
            matched_weight += weight
        else:
            missing.append(skill)

    # Calculate weighted skill score
    skill_score = int((matched_weight / total_weight) * 100) if total_weight != 0 else 0

    # 4. Semantic Analysis
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_processed, jd_processed])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        semantic_score = int(similarity * 100)
    except:
        semantic_score = 0

    # Hybrid Final Score
    final_score = int((skill_score * 0.6) + (semantic_score * 0.4))

    return final_score, matched, missing