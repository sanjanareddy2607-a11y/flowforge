content = '''import os
from google import genai
from dotenv import load_dotenv
from nodes.base_node import BaseNode

load_dotenv()

class AINode(BaseNode):
    def run(self, input_data: dict) -> dict:
        prompt_template = self.config.get("prompt", "Summarize this: {input}")
        input_key       = self.config.get("input_key", "text")
        output_key      = self.config.get("output_key", "ai_response")
        model_name      = self.config.get("model", "gemini-2.0-flash")

        input_text   = input_data.get(input_key, str(input_data))
        final_prompt = prompt_template.replace("{input}", str(input_text))

        try:
            client   = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model=model_name,
                contents=final_prompt
            )
            result = response.text
        except Exception as e:
            result = f"AI node error: {str(e)}"

        return {output_key: result}
'''

with open('nodes/ai_node.py', 'w') as f:
    f.write(content)

print('ai_node.py updated successfully')