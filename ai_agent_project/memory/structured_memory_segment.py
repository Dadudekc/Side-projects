import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class StructuredMemorySegment:
    """
    A structured memory record that stores text, metadata, tags, or embeddings
    for advanced retrieval or classification.
    """

    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None):
        """
        Initializes a structured memory record.

        Args:
            text (str): The main textual content to store.
            metadata (Optional[Dict[str, Any]]): Additional descriptive data.
            tags (Optional[List[str]]): Tags/labels for classification or search.
        """
        self.text = text
        self.metadata = metadata or {}
        self.tags = tags or []

    def __repr__(self) -> str:
        return f"<StructuredMemorySegment tags={self.tags}, metadata={self.metadata}>"
