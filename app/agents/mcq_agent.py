from app.a2a_protocol import make_msg
from app.groq_client import ask_groq
import json
import re

class MCQAgent:
    NAME = "mcq_agent"

    def __init__(self, router=None):
        self.router = router

    def handler(self, msg):
        payload = msg.get("payload", {})
        summary = payload.get("summary") or payload.get("topic") or ""
        num = int(payload.get("num_questions", 5))

        mcqs = self.generate_mcqs(summary, num_questions=num)

        return make_msg(
            self.NAME,
            msg.get("from"),
            "response",
            {"mcqs": mcqs},
            job_id=msg["id"]
        )

    def generate_mcqs(self, summary, num_questions=5):
        prompt = f"""
Generate {num_questions} multiple-choice questions based ONLY on the following summary.
Each question must have 4 options and exactly one correct answer.
Return output strictly as a JSON array with objects like:
[{{"q":"...","options":["A","B","C","D"],"answer":"A"}}]

Summary:
{summary}
"""
        raw = ask_groq(prompt, temperature=0.7)

        # Try JSON parse, with fallback cleaning
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            # attempt to extract first JSON array
            m = re.search(r"\[.*\]", raw, flags=re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
        # final fallback: simple placeholder MCQs
        fallback = [
            {"q": "What is the main idea?", "options": ["A", "B", "C", "D"], "answer": "A"}
        ]
        return fallback
