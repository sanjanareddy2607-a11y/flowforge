import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from nodes.base_node import BaseNode

load_dotenv()

class ScrapeNode(BaseNode):
    def run(self, input_data: dict) -> dict:
        query_template = self.config.get("query", "AI news today")
        num_results    = self.config.get("num_results", 5)
        output_key     = self.config.get("output_key", "raw_text")

        today = datetime.now().strftime("%B %d %Y")

        query = query_template.replace("{input}", str(input_data.get("text", "")))
        query = query.replace("{today}", today)

        api_key = os.getenv("SERP_API_KEY")

        params = {
            "q":       query,
            "api_key": api_key,
            "num":     num_results,
            "engine":  "google"
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params)
            data     = response.json()
            results  = data.get("organic_results", [])

            text_chunks = []
            for r in results[:num_results]:
                title   = r.get("title", "")
                snippet = r.get("snippet", "")
                text_chunks.append(f"{title}: {snippet}")

            combined_text = "\n\n".join(text_chunks)

            if not combined_text:
                combined_text = "No results found for this query."

        except Exception as e:
            combined_text = f"Scrape node error: {str(e)}"

        return {output_key: combined_text}
