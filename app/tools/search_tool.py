import os
from app.logger import logger
import httpx

class SearchTool:
    def __init__(self):
        self.api_key = os.getenv("SEARCH_API_KEY")

    def search(self, query, num_results=5):
        logger.info(f"SearchTool: searching for '{query}' (num={num_results})")
        # offline stub (safe for Kaggle submission demo)
        results = []
        for i in range(num_results):
            results.append({
                "title": f"Result {i+1} about {query}",
                "url": f"https://example.com/{query.replace(' ','-')}/{i+1}",
                "snippet": f"Snippet {i+1} summarizing something about {query}."
            })
        return results
