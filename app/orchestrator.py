from app.a2a_protocol import Router, make_msg
from app.logger import logger
from app.agents.planner_agent import PlannerAgent
from app.agents.notes_agent import NotesAgent
from app.agents.mcq_agent import MCQAgent
from app.agents.research_agent import ResearchAgent
from app.agents.publisher_agent import PublisherAgent
from app.memory.memory_bank import MemoryBank

def start_flow(job_id, payload, STATUS, session_store):
    router = Router()

    # instantiate agents
    planner = PlannerAgent(router=router)
    notes = NotesAgent(router=router)
    mcq = MCQAgent(router=router)
    research = ResearchAgent(router=router)
    publisher = PublisherAgent(router=router)

    # register handlers
    router.register(PlannerAgent.NAME, planner.handler)
    router.register(NotesAgent.NAME, notes.handler)
    router.register(MCQAgent.NAME, mcq.handler)
    router.register(ResearchAgent.NAME, research.handler)
    router.register(PublisherAgent.NAME, publisher.handler)

    # create session
    session_store.create(job_id, {"status":"started", "payload": payload})
    STATUS[job_id] = {"status":"started", "progress": 5}

    # 1) client -> planner
    planner_msg = make_msg("client", PlannerAgent.NAME, "request",
                           {"topic": payload.get("topic"), "timeframe": payload.get("timeframe","7 days")},
                           job_id=job_id)
    planner_resp = router.send(planner_msg)
    plan = planner_resp.get("payload", {}).get("plan", "") or payload.get("topic", "")
    STATUS[job_id].update({"plan_saved": True, "progress": 30})

    # 2) planner -> research
    research_msg = make_msg(PlannerAgent.NAME, ResearchAgent.NAME, "request",
                            {"topic": payload.get("topic")},
                            job_id=job_id)
    research_resp = router.send(research_msg)
    results = research_resp.get("payload", {}).get("results", [])
    if not isinstance(results, list):
        results = [{"text": str(results)}]
    STATUS[job_id].update({"research_hits": len(results), "progress": 50})

    # 3) planner -> notes agent (send both topic and any notes)
    notes_text = payload.get("notes", "")
    notes_msg = make_msg(PlannerAgent.NAME, NotesAgent.NAME, "request",
                         {"topic": payload.get("topic"), "notes": notes_text},
                         job_id=job_id)
    notes_resp = router.send(notes_msg)
    summary = notes_resp.get("payload", {}).get("summary", "")
    if not summary:
        summary = "No summary generated."
    STATUS[job_id].update({"summary_chars": len(summary), "progress": 70})

    # 4) notes -> mcq
    mcq_msg = make_msg(NotesAgent.NAME, MCQAgent.NAME, "request", {"summary": summary}, job_id=job_id)
    mcq_resp = router.send(mcq_msg)
    mcqs = mcq_resp.get("payload", {}).get("mcqs", [])
    if not isinstance(mcqs, list):
        mcqs = []
    STATUS[job_id].update({"mcq_count": len(mcqs), "progress": 85})

    # 5) assemble content and publish
    md = f"# {payload.get('topic')}\n\n## Plan\n\n{plan}\n\n## Summary\n\n{summary}\n\n## MCQs\n"
    for i,q in enumerate(mcqs,1):
        # guard if q is string or dict
        if isinstance(q, dict):
            q_text = q.get("q") or q.get("question") or str(q)
            options = q.get("options", [])
            answer = q.get("answer", "")
        else:
            q_text = str(q)
            options = []
            answer = ""
        md += f"\n### Q{i}: {q_text}\n"
        for opt in options:
            md += f"- {opt}\n"
        md += f"**Answer:** {answer}\n"

    pub_msg = make_msg("orchestrator", PublisherAgent.NAME, "request", {"topic": payload.get("topic"), "content": md}, job_id=job_id)
    pub_resp = router.send(pub_msg)
    path = pub_resp.get("payload", {}).get("path", "")

    STATUS[job_id].update({"publish_path": path, "progress": 100, "status": "done"})

    # persist to MemoryBank
    mb = MemoryBank()
    mb.save_plan(payload.get("user_id","anon"), payload.get("topic"), path)

    # Return final output including summary + MCQs
    return {
        "plan": plan,
        "summary": summary,
        "mcqs": mcqs,
        "publish_path": path,
        "summary_chars": len(summary),
        "mcq_count": len(mcqs)
    }
