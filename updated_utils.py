import fitz
import docx
import re
import spacy
import nltk
from sentence_transformers import SentenceTransformer, util

# ---------------- LOAD MODELS ----------------

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# ---------------- CONFIG ----------------

IMPORTANCE_KEYWORDS = {
    3: ["must", "mandatory", "required", "need", "essential"],
    2: ["strong", "solid", "proven", "preferred"],
    1: ["nice to have", "optional", "plus"]
}

GENERIC_WORDS = {
    "experience", "knowledge", "ability",
    "role", "position", "candidate",
    "responsibility", "requirement",
    "requirements", "skills", "skill",
    "demand"
}

SIMILARITY_THRESHOLD = 0.45

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
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------- REQUIREMENT SENTENCES ----------------

def extract_requirement_sentences(jd_text):
    sentences = nltk.sent_tokenize(jd_text)

    triggers = [
        "require", "required", "must",
        "need", "looking for",
        "should have", "nice to have",
        "preferred"
    ]

    filtered = [
        s for s in sentences
        if any(trigger in s.lower() for trigger in triggers)
    ]

    return filtered if filtered else sentences

# ---------------- SKILL PHRASE EXTRACTION ----------------

def extract_skill_phrases(sentence):
    doc = nlp(sentence)
    phrases = set()

    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()

        if len(phrase.split()) <= 4:
            if not any(word in GENERIC_WORDS for word in phrase.split()):
                phrases.add(phrase)

    # Remove sub-phrases
    cleaned = set()
    for phrase in phrases:
        if not any(
            phrase != other and phrase in other
            for other in phrases
        ):
            cleaned.add(phrase)

    return list(cleaned)

# ---------------- IMPORTANCE WEIGHT ----------------

def get_sentence_weight(sentence):
    sentence_lower = sentence.lower()

    for weight, keywords in IMPORTANCE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in sentence_lower:
                return weight

    return 2

# ---------------- MATCH ENGINE ----------------

def calculate_match_score(resume_text, jd_text):

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    requirement_sentences = extract_requirement_sentences(jd_clean)

    skill_data = []

    for sentence in requirement_sentences:
        weight = get_sentence_weight(sentence)
        phrases = extract_skill_phrases(sentence)

        for phrase in phrases:
            skill_data.append((phrase, weight))

    # Deduplicate while keeping highest weight
    skill_dict = {}
    for phrase, weight in skill_data:
        if phrase not in skill_dict:
            skill_dict[phrase] = weight
        else:
            skill_dict[phrase] = max(skill_dict[phrase], weight)

    if not skill_dict:
        return 0, [], []

    resume_embedding = model.encode(resume_clean, convert_to_tensor=True)

    matched = []
    missing = []

    total_weight = 0
    matched_weight = 0

    for phrase, weight in skill_dict.items():

        phrase_embedding = model.encode(phrase, convert_to_tensor=True)
        similarity = util.cos_sim(phrase_embedding, resume_embedding).item()

        total_weight += weight

        if similarity > SIMILARITY_THRESHOLD:
            matched.append(phrase)
            matched_weight += weight
        else:
            missing.append(phrase)

    # ---------------- PRIMARY SCORE ----------------
    skill_score = int((matched_weight / total_weight) * 100)

    # ---------------- CONTEXT BONUS ----------------
    bonus = 0
    for skill in matched:
        count = resume_clean.count(skill)
        if count > 1:
            bonus += min(5, count)

    final_score = min(100, skill_score + bonus)

    return final_score, matched, missing