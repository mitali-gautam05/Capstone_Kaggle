import os
import datetime
from app.config import OUTPUT_DIR

def sanitize_filename(name):
    name = str(name or "output")
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(c if c in keep else "_" for c in name).strip().replace(" ", "_")

def save_markdown(topic, content):
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"{sanitize_filename(topic)}_{ts}.md"
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
