# nodes/filter_node.py

# WHAT THIS DOES:
# Checks if the data meets a condition before continuing the pipeline.
# Example: Only continue if the AI response is longer than 50 characters.
# Example: Only continue if a keyword exists in the text.

from nodes.base_node import BaseNode

class FilterNode(BaseNode):
    """
    Conditional filter — stops the pipeline if condition not met.
    
    Config options:
        condition   : "contains_keyword", "min_length", "not_empty"
        input_key   : Which key to check
        keyword     : For "contains_keyword" condition
        min_length  : For "min_length" condition
    
    Example config:
        {
            "id": "quality_check",
            "type": "filter",
            "config": {
                "condition": "min_length",
                "input_key": "summary",
                "min_length": 100
            }
        }
    """

    def run(self, input_data: dict) -> dict:
        condition = self.config.get("condition", "not_empty")
        input_key = self.config.get("input_key", "text")
        value     = str(input_data.get(input_key, ""))

        passed = False  # Default: condition fails

        if condition == "not_empty":
            passed = len(value.strip()) > 0

        elif condition == "min_length":
            min_len = self.config.get("min_length", 50)
            passed  = len(value) >= min_len

        elif condition == "contains_keyword":
            keyword = self.config.get("keyword", "").lower()
            passed  = keyword in value.lower()

        # Pass all original data forward + add filter result
        result = dict(input_data)  # Copy everything from previous node
        result["filter_passed"] = passed
        result["filter_message"] = "PASSED" if passed else f"FAILED: condition '{condition}' not met"

        return result 