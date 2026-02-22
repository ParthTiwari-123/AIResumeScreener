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

# ---------------- ENTITY RULER (EXPANDED SKILLS) ----------------
if "entity_ruler" not in nlp.pipe_names:
    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = [

        # ---------- PROGRAMMING ----------
        {"label": "SKILL", "pattern": [{"LOWER": "python"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "java"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "c++"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "c#"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "javascript"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "typescript"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "go"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "ruby"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "php"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "swift"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "kotlin"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "rust"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "nodejs"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "express"}]},

        # ---------- DATA ----------
        {"label": "SKILL", "pattern": [{"LOWER": "machine"}, {"LOWER": "learning"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "deep"}, {"LOWER": "learning"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "data"}, {"LOWER": "analysis"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "data"}, {"LOWER": "science"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "sql"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "mysql"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "postgresql"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "mongodb"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "pandas"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "numpy"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "tensorflow"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "pytorch"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "scikit-learn"}]},

        # ---------- CLOUD & DEVOPS ----------
        {"label": "SKILL", "pattern": [{"LOWER": "docker"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "kubernetes"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "aws"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "azure"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "gcp"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "devops"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "git"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "jenkins"}]},

        # ---------- FRONTEND ----------
        {"label": "SKILL", "pattern": [{"LOWER": "react"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "angular"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "vue"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "html"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "css"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "bootstrap"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "tailwind"}]},

        # ---------- BUSINESS ----------
        {"label": "SKILL", "pattern": [{"LOWER": "project"}, {"LOWER": "management"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "leadership"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "communication"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "teamwork"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "financial"}, {"LOWER": "analysis"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "accounting"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "excel"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "powerpoint"}]},

        # ---------- MARKETING ----------
        {"label": "SKILL", "pattern": [{"LOWER": "seo"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "digital"}, {"LOWER": "marketing"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "content"}, {"LOWER": "marketing"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "branding"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "google"}, {"LOWER": "analytics"}]},

        # ---------- HR ----------
        {"label": "SKILL", "pattern": [{"LOWER": "recruitment"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "talent"}, {"LOWER": "acquisition"}]},
        {"label": "SKILL", "pattern": [{"LOWER": "employee"}, {"LOWER": "engagement"}]},
    ]

    ruler.add_patterns(patterns)

# ---------------- SENTENCE TRANSFORMER ----------------
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

SIMILARITY_THRESHOLD = 0.55

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

    # Only capture defined SKILL entities
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            phrases.add(ent.text.lower())

    return list(phrases)


# ---------------- ENGINE ----------------
def calculate_match_score(resume_text, jd_text):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    resume_sentences = nltk.sent_tokenize(resume_clean)
    if not resume_sentences:
        return 0, [], []

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

    if not skill_dict:
        return 0, [], []

    matched, missing = [], []
    total_w, matched_w = 0, 0

    for phrase, weight in skill_dict.items():
        phrase_embedding = model.encode(phrase, convert_to_tensor=True)
        cos_scores = util.cos_sim(phrase_embedding, resume_embeddings)[0]
        max_sim = cos_scores.max().item()

        total_w += weight

        if max_sim > SIMILARITY_THRESHOLD or phrase in resume_clean:
            matched.append(phrase)
            matched_w += weight
        else:
            missing.append(phrase)

    skill_score = int((matched_w / total_w) * 100) if total_w > 0 else 0

    # Hybrid Score
    full_resume_emb = model.encode(resume_clean, convert_to_tensor=True)
    full_jd_emb = model.encode(jd_clean, convert_to_tensor=True)
    semantic_overall = util.cos_sim(full_resume_emb, full_jd_emb).item()

    final_score = int((skill_score * 0.7) + (semantic_overall * 30))

    return min(100, final_score), matched, missing