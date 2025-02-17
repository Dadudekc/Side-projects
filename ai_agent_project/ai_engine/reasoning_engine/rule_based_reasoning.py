import logging
import re

class RuleBasedReasoning:
    """
    Internal rule-based reasoning engine that applies predefined logic rules.

    Features:
      - Detects cause-effect patterns.
      - Uses conditional reasoning (if X then Y).
      - Can be extended with additional rules.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Each rule is a tuple: (regex pattern, function to handle it)
        self.rules = [
            (r"impact of (.+?) on (.+)", self.reason_cause_effect),
            (r"relationship between (.+?) and (.+)", self.reason_relationship),
            (r"should I (.+?) if (.+)", self.reason_decision_making)
        ]

    def reason(self, prompt: str) -> str:
        """
        Processes the input prompt using pattern-based rules.
        """
        self.logger.debug("Processing rule-based reasoning for: %s", prompt)
        for pattern, method in self.rules:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                self.logger.debug("Matched pattern: %s", pattern)
                return method(*match.groups())
        return "No logical inference found."

    def reason_cause_effect(self, cause: str, effect: str) -> str:
        """
        Handles reasoning of the form 'impact of X on Y'.
        """
        return f"The {cause} directly influences {effect}. Consider factors such as time, intensity, and context."

    def reason_relationship(self, entity1: str, entity2: str) -> str:
        """
        Handles reasoning of the form 'relationship between X and Y'.
        """
        return f"{entity1} and {entity2} interact based on historical trends, mutual dependencies, and systemic influences."

    def reason_decision_making(self, action: str, condition: str) -> str:
        """
        Handles reasoning of the form 'should I do X if Y'.
        """
        return f"Evaluating '{action}' under the condition '{condition}': Prioritize based on risk-reward and situational awareness."
