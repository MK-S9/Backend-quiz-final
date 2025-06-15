
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def generate_questions(text, max_questions=10):
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 20]
    random.shuffle(lines)
    questions = []
    for line in lines[:max_questions]:
        words = line.split()
        if len(words) < 6:
            continue
        answer = words[-1].strip(".,:;-")
        question_text = " ".join(words[:-1]) + " ____?"
        distractors = random.sample(words[:-1], k=min(3, len(words)-1))
        options = [answer] + distractors
        random.shuffle(options)
        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer
        })
    return questions

@app.post("/upload")
async def upload(pdf: UploadFile = File(...)):
    try:
        file_bytes = await pdf.read()
        text = extract_text_from_pdf(file_bytes)
        questions = generate_questions(text)
        return {"questions": questions}
    except Exception as e:
        return {"questions": [], "error": str(e)}
