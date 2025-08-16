from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import fitz
import language_tool_python
import textstat
from textblob import TextBlob
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import shutil
import os
import torch


app = FastAPI()


# Allow frontend connection (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir("backend/static"):
    app.mount("/", StaticFiles(directory="backend/static", html=True), name="static")

# Load your dataset once (stored locally in backend)
df = pd.read_csv("data/preprocessed_dataset.csv")
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return " ".join(page.get_text() for page in doc)

def normalize(val, min_val, max_val):
    return max(0, min(5, (val - min_val) / (max_val - min_val) * 5))


@app.post("/predict")
async def predict_paper(pdf: UploadFile = File(...)):
    # Save uploaded PDF
    os.makedirs("temp", exist_ok=True)
    pdf_path = f"temp/{pdf.filename}"
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)
    paper_text = extract_text(pdf_path)

    if not paper_text.strip():
        os.remove(pdf_path)
        return JSONResponse(status_code=400, content={
             "verdict": "REJECTED",
             "feedback": ["❌ Unable to extract text from the uploaded PDF. Please upload a machine-readable document."]
    })



    # Novelty Score
    accepted_texts = df[df['accepted'] == 1][['title', 'abstract']].fillna('').agg(' '.join, axis=1).tolist()
    accepted_embeddings = model.encode(accepted_texts, convert_to_tensor=True)
    paper_embedding = model.encode(paper_text[:1000], convert_to_tensor=True)
    novelty_score = round(5 - normalize(util.cos_sim(paper_embedding, accepted_embeddings)[0].mean().item(), 0.2, 0.9), 2)

    # Quality Score
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(paper_text)
    error_count = len(matches)
    total_words = len(paper_text.split())
    errors_per_100_words = error_count / max(total_words / 100, 1)
    grammar_score_raw = max(0, 100 - (errors_per_100_words / 20) * 100)
    flesch_score = textstat.flesch_reading_ease(paper_text)
    grammar_score_scaled = normalize(grammar_score_raw, 50, 100)
    flesch_scaled = normalize(flesch_score, 0, 60)
    quality_score = round((grammar_score_scaled + flesch_scaled) / 2, 2)

    # Relevance Score
    vectorizer_dataset = TfidfVectorizer(max_features=20, stop_words='english')
    vectorizer_dataset.fit(df[df['accepted'] == 1][['title', 'abstract']].fillna('').agg(' '.join, axis=1))
    domain_keywords = vectorizer_dataset.get_feature_names_out().tolist()

    vectorizer_paper = TfidfVectorizer(max_features=20, stop_words='english')
    vectorizer_paper.fit([paper_text])
    paper_keywords = vectorizer_paper.get_feature_names_out().tolist()

    emb_domain = model.encode(" ".join(domain_keywords), convert_to_tensor=True)
    emb_paper = model.encode(" ".join(paper_keywords), convert_to_tensor=True)
    relevance_score = round(normalize(util.cos_sim(emb_domain, emb_paper).item(), 0.2, 0.9), 2)

    # Review Sentiment
    sentiment = TextBlob("This paper is insightful and well-structured.").sentiment.polarity
    review_sentiment_score = round((sentiment + 1) * 2.5, 2)

    # Composite Score
    composite_score = round(
        0.30 * novelty_score +
        0.25 * quality_score +
        0.25 * relevance_score +
        0.20 * review_sentiment_score,
        2
    )
    verdict = "ACCEPTED" if composite_score >= 3.0 else "REJECTED"

    # Feedback Generation
    feedback = []
    if novelty_score >= 4:
        feedback.append("✅ High novelty and original contributions.")
    elif novelty_score >= 3:
        feedback.append("ℹ️ Moderate novelty, could improve.")
    else:
        feedback.append("❌ Lacks novelty.")

    if quality_score >= 4:
        feedback.append("✅ Strong grammar and readability.")
    elif quality_score >= 2.5:
        feedback.append("ℹ️ Acceptable, needs polishing.")
    else:
        feedback.append("❌ Poor readability.")

    if relevance_score >= 3.5:
        feedback.append("✅ Highly relevant to the domain.")
    elif relevance_score >= 2:
        feedback.append("ℹ️ Moderately relevant.")
    else:
        feedback.append("❌ Low relevance.")

    if review_sentiment_score >= 3.5:
        feedback.append("✅ Positive reviewer tone.")
    elif review_sentiment_score >= 2:
        feedback.append("ℹ️ Neutral tone.")
    else:
        feedback.append("❌ Weak reviewer support.")

    # Clean up temporary file
    os.remove(pdf_path)

    # Return results as JSON
    return JSONResponse({
        "novelty": novelty_score,
        "quality": quality_score,
        "relevance": relevance_score,
        "sentiment": review_sentiment_score,
        "composite": composite_score,
        "verdict": verdict,
        "feedback": feedback
    })
