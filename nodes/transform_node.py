# nodes/transform_node.py

# WHAT THIS DOES:
# Takes the previous node's output and reshapes it.
# Examples:
#   - Extract just one key from a dict
#   - Truncate text to a max length
#   - Add a prefix/suffix to text
#   - Combine multiple keys into one

from nodes.base_node import BaseNode

class TransformNode(BaseNode):
    """
    Data transformation node — reshapes data between pipeline stages.
    
    Config options:
        operation   : What to do. Options: "extract_key", "truncate", "combine", "prefix"
        input_key   : Which key from input_data to operate on
        output_key  : What to name the result
        max_length  : For "truncate" operation
        prefix      : For "prefix" operation
        keys        : For "combine" operation — list of keys to join
    
    Example config:
        {
            "id": "clean_output",
            "type": "transform",
            "config": {
                "operation": "truncate",
                "input_key": "ai_response",
                "output_key": "final_text",
                "max_length": 500
            }
        }
    """

    def run(self, input_data: dict) -> dict:
        operation  = self.config.get("operation", "extract_key")
        input_key  = self.config.get("input_key", "text")
        output_key = self.config.get("output_key", "transformed")

        if operation == "extract_key":
            # Just pull one key out and rename it
            value = input_data.get(input_key, "")
            return {output_key: value}

        elif operation == "truncate":
            # Cut text to a max character length
            max_length = self.config.get("max_length", 500)
            value      = str(input_data.get(input_key, ""))
            return {output_key: value[:max_length]}

        elif operation == "combine":
            # Join multiple keys into one text block
            keys   = self.config.get("keys", [input_key])
            parts  = [str(input_data.get(k, "")) for k in keys]
            combined = "\n\n".join(parts)
            return {output_key: combined}

        elif operation == "prefix":
            # Add a fixed text before the value
            prefix = self.config.get("prefix", "")
            value  = str(input_data.get(input_key, ""))
            return {output_key: prefix + value}

        else:
            # Unknown operation — pass through unchanged
            return {output_key: input_data.get(input_key, "")}