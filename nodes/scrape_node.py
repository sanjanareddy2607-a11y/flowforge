# nodes/scrape_node.py

# WHAT THIS DOES:
# Searches Google (via SerpAPI) for a query and returns the top results
# as text that the next node (usually an AI node) can process.

# WHY SERPAPI:
# Direct Google scraping is against ToS and breaks often.
# SerpAPI gives you clean JSON search results legally.
# Free tier = 100 searches/month, plenty for a demo.

import os
import requests
from dotenv import load_dotenv
from nodes.base_node import BaseNode

load_dotenv()

class ScrapeNode(BaseNode):
    """
    Fetches search results from SerpAPI.
    
    Config options:
        query       : Search query string. Can use {input} to inject previous output.
        num_results : How many results to fetch (default 5).
        output_key  : Key name for results in output dict (default "raw_text").
    
    Example config:
        {
            "id": "fetch_news",
            "type": "scrape",
            "config": {
                "query": "latest AI startup funding news",
                "num_results": 5,
                "output_key": "raw_text"
            }
        }
    """

    def run(self, input_data: dict) -> dict:
        # Step 1: Read config
        query_template = self.config.get("query", "AI news today")
        num_results    = self.config.get("num_results", 5)
        output_key     = self.config.get("output_key", "raw_text")

        # Step 2: Replace {input} if previous node's output should shape the query
        # e.g., previous node extracted a company name, now we search for that company
        query = query_template.replace("{input}", str(input_data.get("text", "")))

        # Step 3: Build SerpAPI request
        api_key = os.getenv("SERP_API_KEY")
        
        params = {
            "q":      query,       # the search query
            "api_key": api_key,    # your SerpAPI key
            "num":    num_results, # number of results
            "engine": "google"     # which search engine to use
        }

        try:
            # Step 4: Make the HTTP GET request to SerpAPI
            response = requests.get("https://serpapi.com/search", params=params)
            data     = response.json()

            # Step 5: Extract organic search results
            # SerpAPI returns results under "organic_results" key
            results      = data.get("organic_results", [])
            
            # Step 6: Pull out title + snippet from each result and combine
            # snippet = short description text shown under Google search results
            text_chunks  = []
            for r in results[:num_results]:
                title   = r.get("title", "")
                snippet = r.get("snippet", "")
                text_chunks.append(f"{title}: {snippet}")

            combined_text = "\n\n".join(text_chunks)

        except Exception as e:
            combined_text = f"Scrape node error: {str(e)}"

        # Step 7: Return combined text for next node
        return {output_key: combined_text} 