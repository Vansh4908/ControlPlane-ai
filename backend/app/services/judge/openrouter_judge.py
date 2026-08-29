from app.services.llm.openrouter_service import OpenRouterService
from app.services.llm.llm_judge import LLMJudge


class OpenRouterJudge:

    def __init__(self, model):
        self.judge = LLMJudge(
            OpenRouterService(),
            model
        )

    def evaluate(
        self,
        prompt,
        ai_response,
        judge_name,
        evaluation_criteria,
        context=None
    ):
        return self.judge.evaluate(
            prompt,
            ai_response,
            judge_name,
            evaluation_criteria,
            context=context
        )