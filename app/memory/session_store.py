# simple in-memory session store for ongoing jobs
class SessionStore:
    def __init__(self):
        self.sessions = {}

    def create(self, job_id, initial):
        self.sessions[job_id] = initial

    def update(self, job_id, key, value):
        if job_id in self.sessions:
            self.sessions[job_id][key] = value

    def get(self, job_id):
        return self.sessions.get(job_id)
