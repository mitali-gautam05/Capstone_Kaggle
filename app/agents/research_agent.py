from app.a2a_protocol import make_msg
from app.groq_client import ask_groq

class ResearchAgent:
    NAME = "research_agent"

    def __init__(self, router=None):
        self.router = router

    def handler(self, msg):
        payload = msg.get("payload", {})
        topic = payload.get("topic") or msg.get("text", "") or ""

        research_text = self.generate_research(topic)

        # Return as list for orchestrator expectations
        return make_msg(
            self.NAME,
            msg.get("from"),
            "response",
            {"results": [{"text": research_text}]},
            job_id=msg["id"]
        )

    def generate_research(self, topic):
        prompt = f"""
Research the following topic and provide factual, concise information and key ideas.

Topic: {topic}

Include:
- Short overview
- Key concepts
- Common use-cases or examples
- Important formulas or facts (if any)
"""
        return ask_groq(prompt)
