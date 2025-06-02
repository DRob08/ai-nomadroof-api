import json
from pathlib import Path
from rapidfuzz import process, fuzz

FAQ_PATH = Path(__file__).parent.parent / "data" / "faq.json"

def load_faq():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def find_answer_from_faq(question: str, cutoff: float = 60.0):  # cutoff in percent
    faqs = load_faq()
    questions = [faq['question'] for faq in faqs]

    match = process.extractOne(
        question, 
        questions, 
        scorer=fuzz.token_set_ratio,  # Better for natural language
        score_cutoff=cutoff
    )

    if match:
        matched_question, score, _ = match
        for faq in faqs:
            if faq["question"] == matched_question:
                return faq["answer"]
    return None
