from openai import OpenAI

from app.config import Config


class GroqService:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured")

        self.client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            timeout=12.0
        )

    def generate_response(
        self,
        prompt,
        model_name,
        response_format=None
    ):
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format=response_format
        )

        if not response or not getattr(response, "choices", None):
            return None

        return response.choices[0].message.content