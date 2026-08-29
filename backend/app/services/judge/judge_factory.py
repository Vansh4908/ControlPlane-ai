from app.services.judge.gemini_judge import GeminiJudge
from app.services.judge.groq_judge import GroqJudge
from app.services.judge.openrouter_judge import OpenRouterJudge


class JudgeFactory:

    @staticmethod
    def create(provider, model):
        provider = provider.lower()

        if provider == "gemini":
            return GeminiJudge(model)

        if provider == "groq":
            return GroqJudge(model)

        if provider == "openrouter":
            return OpenRouterJudge(model)

        raise ValueError(
            f"Unsupported judge provider: {provider}"
        )