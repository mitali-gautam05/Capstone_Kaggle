"""
Simple A2A (Agent-to-Agent) protocol and router.
Messages are JSON dicts with:
{
  "id": "<job-id>",
  "from": "<agent-name>",
  "to": "<agent-name>",
  "type": "request"|"response"|"event",
  "payload": { ... }
}
"""

import uuid
from app.logger import logger

def make_msg(from_agent, to_agent, msg_type, payload, job_id=None):
    return {
        "id": job_id or str(uuid.uuid4()),
        "from": from_agent,
        "to": to_agent,
        "type": msg_type,
        "payload": payload
    }

class Router:
    def __init__(self):
        # simple registry to call agent handlers directly
        self.handlers = {}

    def register(self, agent_name, handler_func):
        self.handlers[agent_name] = handler_func

    def send(self, msg):
        to = msg.get("to")
        handler = self.handlers.get(to)
        if not handler:
            logger.error(f"No handler registered for {to}")
            return {"error":"no_handler", "msg": msg}
        logger.info(f"A2A: routing {msg['type']} from {msg['from']} -> {to}")
        return handler(msg)
