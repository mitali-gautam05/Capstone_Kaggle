from app.a2a_protocol import make_msg
from app.groq_client import ask_groq

class PlannerAgent:
    NAME = "planner_agent"

    def __init__(self, router=None):
        self.router = router

    def handler(self, msg):
        payload = msg.get("payload", {})
        topic = payload.get("topic") or msg.get("text", "") or "General Study"
        timeframe = payload.get("timeframe", "7 days")

        plan = self.generate_plan(topic, timeframe)

        return make_msg(
            self.NAME,
            msg.get("from"),
            "response",
            {"plan": plan},
            job_id=msg["id"]
        )

    def generate_plan(self, topic, timeframe):
        # Use Groq to generate a plan for better quality (not hardcoded)
        prompt = f"""
Create a concise step-by-step study plan for the following topic.

Topic: {topic}
Timeframe: {timeframe}

Include:
- 5 major subtopics to cover
- Daily breakdown or milestones
- Suggested practice activities
Return the plan as plain text.
"""
        return ask_groq(prompt)
