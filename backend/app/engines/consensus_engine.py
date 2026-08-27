class ConsensusEngine:

    RECOMMENDATION_PRIORITY = {
        "ALLOW": 0,
        "REVIEW": 1,
        "BLOCK": 2
    }

    def calculate(self, judge_results):
        if not judge_results:
            raise ValueError("At least one judge result is required")

        total_confidence = sum(
            result.confidence
            for result in judge_results
        )

        if total_confidence == 0:
            overall_risk = 0.0
        else:
            overall_risk = sum(
                result.overall_risk * result.confidence
                for result in judge_results
            ) / total_confidence

        overall_confidence = sum(
            result.confidence
            for result in judge_results
        ) / len(judge_results)

        recommendation = max(
            (
                result.recommendation
                for result in judge_results
            ),
            key=lambda value: self.RECOMMENDATION_PRIORITY[value]
        )

        return {
            "overall_risk": round(overall_risk, 4),
            "confidence": round(overall_confidence, 4),
            "recommendation": recommendation,
            "judge_count": len(judge_results)
        }