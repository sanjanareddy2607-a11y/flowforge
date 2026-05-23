# nodes/ai_node.py


import os
import google.generativeai as genai
from dotenv import load_dotenv
from nodes.base_node import BaseNode

# load_dotenv() reads your .env file and makes the keys available via os.getenv()
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AINode(BaseNode):
    """
    Calls Google Gemini API with a prompt + previous node's output.
    
    Config options (what you write in your workflow JSON):
        prompt      : The instruction to give Gemini. Use {input} as placeholder
                      for the previous node's output.
        input_key   : Which key from the previous node's output to use.
                      Default is "text".
        output_key  : What to name the output in the result dict.
                      Default is "ai_response".
        model       : Gemini model to use. Default is "gemini-2.5-flash" (fast + cheap).
    
    Example config in workflow JSON:
        {
            "id": "summarize",
            "type": "ai",
            "config": {
                "prompt": "Summarize this in 3 bullet points: {input}",
                "input_key": "raw_text",
                "output_key": "summary"
            }
        }
    """

    def run(self, input_data: dict) -> dict:
        # Step 1: Read config values, use defaults if not provided
        prompt_template = self.config.get("prompt", "Summarize this: {input}")
        input_key       = self.config.get("input_key", "text")
        output_key      = self.config.get("output_key", "ai_response")
        model_name      = self.config.get("model", "gemini-2.5-flash")

        # Step 2: Get the actual input text from the previous node's output
        # If the key doesn't exist, we convert the whole dict to a string as fallback
        input_text = input_data.get(input_key, str(input_data))

        # Step 3: Replace {input} placeholder in the prompt with actual text
        # This is basic prompt templating — a core concept in AI engineering
        final_prompt = prompt_template.replace("{input}", str(input_text))

        # Step 4: Call Gemini API
        try:
            model    = genai.GenerativeModel(model_name)
            response = model.generate_content(final_prompt)
            result   = response.text  # The AI's reply as a plain string

        except Exception as e:
            # If the API call fails, we don't crash the whole pipeline
            # We return an error message so the next node still gets something
            result = f"AI node error: {str(e)}"

        # Step 5: Return result as a dict so the next node can use it
        return {output_key: result}