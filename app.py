
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from typing import List
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def generate_questions(text: str, count: int = 5) -> List[dict]:
    sentences = [s.strip() for s in text.split('.') if len(s.split()) > 6]
    random.shuffle(sentences)
    questions = []
    for s in sentences[:count]:
        words = s.split()
        if len(words) < 6:
            continue
        blank_index = random.randint(2, len(words) - 2)
        answer = words[blank_index]
        words[blank_index] = "_____"
        question = " ".join(words)
        options = [answer] + random.sample(words, k=min(3, len(words)))
        random.shuffle(options)
        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })
    return questions

@app.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    try:
        file_bytes = await pdf.read()
        text = extract_text_from_pdf(file_bytes)
        questions = generate_questions(text)
        return {"questions": questions}
    except Exception as e:
        return {"questions": [], "error": str(e)}
