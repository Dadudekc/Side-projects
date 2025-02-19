import logging
from typing import Optional, Dict, Any

# If you plan to make real requests, ensure "requests" is installed.
# Otherwise, we fallback to a simulated response.
try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AIClient:
    """
    AIClient provides multiple AI-based methods used in the debugging workflow:

    - send_prompt: Sends arbitrary prompts to a real or simulated AI service.
    - evaluate_patch_with_reason: Evaluates a code patch for correctness, returning a score and explanation.
    - refine_patch: Attempts to improve a patch automatically.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the AIClient.

        Args:
            base_url: (optional) The API endpoint for a real AI service.
            api_key: (optional) An API key for authenticating with a real AI service.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url
        self.api_key = api_key

    def send_prompt(self, prompt: str) -> str:
        """
        Sends a prompt to an AI model and returns the model's response.
        If no real endpoint is configured, returns a simulated response.

        Args:
            prompt: The input prompt to send to the AI.

        Returns:
            The AI-generated or simulated response.
        """
        self.logger.debug("Sending prompt to AI model: %s", prompt)
        if self.base_url and requests:
            headers: Dict[str, str] = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            try:
                response = requests.post(
                    self.base_url,
                    json={"prompt": prompt},
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                data: Dict[str, Any] = response.json()
                self.logger.debug("Received AI response data: %s", data)
                return data.get("response", "")
            except Exception as e:
                self.logger.error("Error contacting AI service: %s", e)
                return "Error contacting AI service."
        else:
            self.logger.debug("Simulating AI response.")
            return f"Simulated response for prompt: '{prompt}'"

    def evaluate_patch_with_reason(self, patch: str) -> Dict[str, Any]:
        """
        Evaluates the patch and returns a dictionary containing:
            - 'score': (int) A numeric score indicating the patch's correctness (0-100).
            - 'reason': (str) An explanation for the assigned score.

        Args:
            patch: The code patch to evaluate.

        Returns:
            A dictionary with keys {"score", "reason"}.
        """
        self.logger.debug("Evaluating patch:\n%s", patch)
        # Simple logic: if patch includes "fixed code", it is considered better.
        if "fixed code" in patch:
            return {"score": 80, "reason": "Patch appears to fix the issue well."}
        else:
            return {"score": 40, "reason": "Patch does not seem to address the problem."}

    def refine_patch(self, patch: str) -> str:
        """
        Attempts to refine a given patch. Returns the refined patch if successful.
        Returns an empty string if no refinement is possible.

        Args:
            patch: The original patch to refine.

        Returns:
            The refined patch (str) or an empty string if unsuccessful.
        """
        self.logger.debug("Refining patch:\n%s", patch)
        if "fixed code" in patch:
            # Replace 'fixed code' with 'refined code' as a trivial example.
            return patch.replace("fixed code", "refined code")
        return ""
