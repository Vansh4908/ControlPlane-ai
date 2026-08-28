class PolicyEngine:

    ACTION_MAP = {
        "ALLOW": "ALLOW",
        "REVIEW": "REVIEW",
        "FLAG": "REVIEW",
        "BLOCK": "BLOCK",
        "EDIT": "REVIEW"
    }

    def _normalize_action(self, action):
        if not action:
            return None

        return self.ACTION_MAP.get(
            action.upper(),
            None
        )

    def decide(self, risk_assessment, policy):
        """
        Convert risk assessment + application policy
        into a governance decision.
        """

        dominant_category = risk_assessment["dominant_category"]
        dominant_score = risk_assessment["dominant_score"]

        policy_action = None

        if dominant_category == "privacy":
            policy_action = self._normalize_action(
                policy.pii_action
            )

        elif dominant_category == "hallucination":
            policy_action = self._normalize_action(
                policy.hallucination_action
            )

        elif dominant_category == "bias":
            policy_action = self._normalize_action(
                policy.bias_action
            )

        if policy_action is None:

            risk_level = risk_assessment["risk_level"]

            if risk_level == "CRITICAL":
                policy_action = "BLOCK"

            elif risk_level == "HIGH":
                policy_action = "REVIEW"

            else:
                policy_action = "ALLOW"

        return {
            "decision": policy_action,
            "dominant_category": dominant_category,
            "dominant_score": dominant_score,
            "risk_level": risk_assessment["risk_level"],
            "confidence": risk_assessment["confidence"],
            "policy_id": policy.id,
            "policy_name": policy.name,
            "reason": (
                f"{dominant_category.capitalize()} risk "
                f"was assessed at {dominant_score:.2f}. "
                f"Policy '{policy.name}' requires "
                f"{policy_action}."
            )
        }