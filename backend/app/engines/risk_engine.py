class RiskEngine:

    RISK_LEVELS = {
        "LOW": 0.30,
        "MEDIUM": 0.60,
        "HIGH": 0.80,
        "CRITICAL": 1.01
    }

    def _risk_level(self, score):
        if score < self.RISK_LEVELS["LOW"]:
            return "LOW"

        if score < self.RISK_LEVELS["MEDIUM"]:
            return "MEDIUM"

        if score < self.RISK_LEVELS["HIGH"]:
            return "HIGH"

        return "CRITICAL"

    def _weighted_average(self, values):
        if not values:
            return 0.0

        total_weight = sum(
            confidence
            for _, confidence in values
        )

        if total_weight == 0:
            return sum(
                score
                for score, _ in values
            ) / len(values)

        return sum(
            score * confidence
            for score, confidence in values
        ) / total_weight

    def analyze(
        self,
        judge_results,
        consensus,
        pii_result=None
    ):
        if not judge_results:
            raise ValueError(
                "At least one judge result is required"
            )

        # ---------------------------------------------------------
        # 1. LLM judge risk signals
        # ---------------------------------------------------------

        safety_scores = [
            (result.overall_risk, result.confidence)
            for result in judge_results
        ]

        hallucination_scores = [
            (result.hallucination_score, result.confidence)
            for result in judge_results
        ]

        bias_scores = [
            (result.bias_score, result.confidence)
            for result in judge_results
        ]

        privacy_scores = [
            (result.privacy_score, result.confidence)
            for result in judge_results
        ]

        category_scores = {
            "safety": round(
                self._weighted_average(safety_scores),
                4
            ),
            "hallucination": round(
                self._weighted_average(hallucination_scores),
                4
            ),
            "bias": round(
                self._weighted_average(bias_scores),
                4
            ),
            "privacy": round(
                self._weighted_average(privacy_scores),
                4
            )
        }

        # ---------------------------------------------------------
        # 2. Deterministic PII signal
        # ---------------------------------------------------------

        pii_detected = (
            pii_result
            and pii_result.get("has_pii", False)
        )

        if pii_detected:
            category_scores["privacy"] = max(
                category_scores["privacy"],
                1.0
            )

        # ---------------------------------------------------------
        # 3. Identify dominant risk
        # ---------------------------------------------------------

        dominant_category = max(
            category_scores,
            key=category_scores.get
        )

        dominant_score = category_scores[
            dominant_category
        ]

        # ---------------------------------------------------------
        # 4. Overall risk
        # ---------------------------------------------------------

        overall_risk = max(
            consensus["overall_risk"],
            dominant_score
        )

        overall_risk = round(
            overall_risk,
            4
        )

        # ---------------------------------------------------------
        # 5. Confidence
        # ---------------------------------------------------------

        confidence = round(
            consensus["confidence"],
            4
        )

        return {
            "overall_risk": overall_risk,
            "risk_level": self._risk_level(
                overall_risk
            ),
            "confidence": confidence,
            "category_scores": category_scores,
            "dominant_category": dominant_category,
            "dominant_score": dominant_score,
            "pii_detected": bool(pii_detected)
        }