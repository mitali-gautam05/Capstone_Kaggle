from app.a2a_protocol import make_msg
from app.tools.file_tool import save_markdown
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PublisherAgent:
    NAME = "publisher_agent"

    def __init__(self, router=None):
        self.router = router

    def handler(self, msg):
        payload = msg.get("payload", {})
        topic = payload.get("topic", "untitled")
        content = payload.get("content", "")

        # Save Markdown
        path = save_markdown(topic, content)

        # ---- HTML Dashboard Output ----
        html_path = path.replace(".md", "__dashboard.html")
        html_content = self._make_html(topic, content)

        # Ensure directory exists
        os.makedirs(os.path.dirname(html_path), exist_ok=True)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # ---- PDF Report Output ----
        pdf_path = path.replace(".md", "__report.pdf")
        self._make_pdf(pdf_path, topic, content)

        # Return A2A protocol message
        return make_msg(
            self.NAME,
            msg.get("from"),
            "response",
            {"path": path},
            job_id=msg["id"]
        )

    # ------------------------------------------------------
    # Generate HTML dashboard
    # ------------------------------------------------------
    def _make_html(self, topic, content):
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{topic} - StudyMate Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}
        h1 {{
            color: #2d6cdf;
        }}
        pre {{
            background: #f4f4f4;
            padding: 20px;
            white-space: pre-wrap;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <h1>{topic} – Dashboard</h1>
    <pre>{content}</pre>
</body>
</html>
"""

    # ------------------------------------------------------
    # Generate PDF report
    # ------------------------------------------------------
    def _make_pdf(self, pdf_path, topic, content):
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, f"{topic} – Report")

        c.setFont("Helvetica", 11)
        y -= 40

        for line in content.split("\n"):
            if y < 40:  # New page if text goes out of space
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 50

            c.drawString(40, y, line)
            y -= 18

        c.save()
