from app.services.llm.groq_service import GroqService
from app.services.llm.llm_judge import LLMJudge


class GroqJudge:

    def __init__(self, model_name):
        self.judge = LLMJudge(
            GroqService(),
            model_name
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