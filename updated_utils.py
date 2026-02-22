import fitz
import docx
import re
import spacy
import nltk
from sentence_transformers import SentenceTransformer, util

# ---------------- MODELS ----------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Intelligent Skill Recognition
if "entity_ruler" not in nlp.pipe_names:
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    patterns = [
        {"label": "TECH", "pattern": "python"},
        {"label": "TECH", "pattern": "java"},
        {"label": "TECH", "pattern": "c++"},
        {"label": "TECH", "pattern": "docker"},
        {"label": "TECH", "pattern": "machine learning"},
        {"label": "TECH", "pattern": "react"},
        {"label": "TECH", "pattern": "node"},
        {"label": "TECH", "pattern": "sql"}
    ]
    ruler.add_patterns(patterns)

# 
model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# ---------------- CONFIG ----------------
IMPORTANCE_KEYWORDS = {
    3: ["must", "mandatory", "required", "need", "essential"],
    2: ["strong", "solid", "proven", "preferred", "efficient"],
    1: ["nice to have", "plus", "like"]
}

# Updated Noise Filter
GENERIC_WORDS = {
    "experience", "knowledge", "ability", "role", "skills", "who", "have", 
    "mandatory", "professionals", "efficient", "looking", "someone"
}
SIMILARITY_THRESHOLD = 0.55 # Contextual threshold

# ---------------- UTILS ----------------
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

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_skill_phrases(sentence):
    doc = nlp(sentence)
    phrases = set()
    for ent in doc.ents:
        if ent.label_ == "TECH":
            phrases.add(ent.text.lower())
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        if not any(word in GENERIC_WORDS for word in phrase.split()):
            if doc[chunk.start].pos_ not in ["PRON", "DET", "ADP"]:
                phrases.add(phrase)
    return list(phrases)

# ---------------- ENGINE ----------------
def calculate_match_score(resume_text, jd_text):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    # Split resume into sentences for better semantic search
    resume_sentences = nltk.sent_tokenize(resume_clean)
    if not resume_sentences: return 0, [], []
    resume_embeddings = model.encode(resume_sentences, convert_to_tensor=True)

    jd_sentences = nltk.sent_tokenize(jd_clean)
    skill_dict = {}

    for sent in jd_sentences:
        weight = 2
        for w, keywords in IMPORTANCE_KEYWORDS.items():
            if any(kw in sent.lower() for kw in keywords):
                weight = w
        phrases = extract_skill_phrases(sent)
        for p in phrases:
            skill_dict[p] = max(skill_dict.get(p, 0), weight)

    if not skill_dict: return 0, [], []

    matched, missing = [], []
    total_w, matched_w = 0, 0

    for phrase, weight in skill_dict.items():
        phrase_embedding = model.encode(phrase, convert_to_tensor=True)
        # Fix: Line was commented out, causing NameError
        cos_scores = util.cos_sim(phrase_embedding, resume_embeddings)[0]
        max_sim = cos_scores.max().item()
        
        total_w += weight
        # 0.55 works better for sentence-to-phrase matching
        if max_sim > SIMILARITY_THRESHOLD or phrase in resume_clean:
            matched.append(phrase)
            matched_w += weight
        else:
            missing.append(phrase)

    skill_score = int((matched_w / total_w) * 100) if total_w > 0 else 0
    
    # Hybrid Final Score
    full_resume_emb = model.encode(resume_clean, convert_to_tensor=True)
    full_jd_emb = model.encode(jd_clean, convert_to_tensor=True)
    semantic_overall = util.cos_sim(full_resume_emb, full_jd_emb).item()
    
    final_score = int((skill_score * 0.7) + (semantic_overall * 30))
    return min(100, final_score), matched, missing