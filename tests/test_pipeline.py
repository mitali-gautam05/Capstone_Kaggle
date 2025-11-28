from app.orchestrator import start_flow
from app.memory.session_store import SessionStore

def test_flow_runs(tmp_path):
    STATUS = {}
    store = SessionStore()
    payload = {"user_id":"test", "topic":"Test Topic", "notes":"Sample notes..."}
    start_flow("testjob", payload, STATUS, store)
    assert STATUS["testjob"]["status"] == "done"
    assert "publish_path" in STATUS["testjob"]
