

from abc import ABC, abstractmethod
# ABC = Abstract Base Class. It lets us define a template that other classes must follow.
# abstractmethod = marks a method that MUST be implemented by child classes.

class BaseNode(ABC):
    """
    Every node inherits from this class.
    This ensures all nodes have the same interface.
    """

    def __init__(self, node_id: str, config: dict):
        # node_id = unique name for this node, e.g. "fetch_news"
        # config  = settings for this node, e.g. {"query": "AI news"}
        self.node_id = node_id
        self.config = config

    @abstractmethod
    def run(self, input_data: dict) -> dict:
        """
        EVERY node must implement this method.
        
        input_data: the output from the PREVIOUS node (or empty dict for first node)
        returns:    a dict containing this node's output
        
        Example:
            input_data  = {"results": ["article 1", "article 2"]}
            returns     = {"summary": "Here are 2 AI articles..."}
        """
        pass