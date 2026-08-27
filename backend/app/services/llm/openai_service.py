from openai import OpenAI

from app.config import Config


class OpenAIService:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY
        )

    def generate_response(self, prompt):
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        return response.output_text