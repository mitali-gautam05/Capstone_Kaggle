from app.a2a_protocol import make_msg
from app.groq_client import ask_groq

class NotesAgent:
    NAME = "notes_agent"

    def __init__(self, router=None):
        self.router = router

    def handler(self, msg):
        payload = msg.get("payload", {})

        # Accept topic and/or notes from orchestrator
        topic = payload.get("topic")
        notes_text = payload.get("notes")

        if topic and not notes_text:
            # If only topic given, create notes from the topic
            text_to_use = topic
        elif notes_text:
            text_to_use = notes_text
        else:
            # fallback
            text_to_use = msg.get("text", "")

        summary = self.generate_notes(text_to_use)

        return make_msg(
            self.NAME,
            msg.get("from"),
            "response",
            {"summary": summary},
            job_id=msg["id"]
        )

    def generate_notes(self, text):
        prompt = f"""
Write clear, student-friendly study notes based on the following input:

{text}

Structure the output with:
- A short definition/overview
- 3–6 key points / subtopics
- Simple example(s)
- A 2–3 line final summary
Return the notes as plain text.
"""
        return ask_groq(prompt)
