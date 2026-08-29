import re


class PIIDetector:

    PATTERNS = {
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),

        "phone": re.compile(
            r"(?<!\d)(?:\+?\d[\d\s()-]{8,}\d)(?!\d)"
        ),

        "credit_card": re.compile(
            r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)"
        ),

        "ip_address": re.compile(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        )
    }

    def detect(self, text):

        if not text:
            return {
                "has_pii": False,
                "detected_types": [],
                "matches": []
            }

        detected_types = []
        matches = []

        for pii_type, pattern in self.PATTERNS.items():

            found = pattern.findall(text)

            if found:
                detected_types.append(pii_type)

                matches.extend(
                    {
                        "type": pii_type,
                        "value": value
                    }
                    for value in found
                )

        return {
            "has_pii": bool(matches),
            "detected_types": detected_types,
            "matches": matches
        }