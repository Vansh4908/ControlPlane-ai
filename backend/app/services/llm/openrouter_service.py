from openai import OpenAI

from app.config import Config


class OpenRouterService:

    def __init__(self):
        if not Config.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=Config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
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

        return response.choices[0].message.content