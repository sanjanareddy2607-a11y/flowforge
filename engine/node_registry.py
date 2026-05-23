# engine/node_registry.py

# WHAT THIS DOES:
# Maps string names (used in JSON config) to actual Python classes.
# This is the "Registry Pattern" — a fundamental software design pattern.

# WHY THIS MATTERS:
# Without this, you'd need giant if/elif chains.
# With this, adding a new node type = adding ONE line to this file.
# Interviewers love this pattern — it's open for extension, closed for modification
# (this is the "Open/Closed Principle" in SOLID design principles).

from nodes.ai_node       import AINode
from nodes.scrape_node   import ScrapeNode
from nodes.transform_node import TransformNode
from nodes.filter_node   import FilterNode
from nodes.email_node    import EmailNode

# The registry: string → class
# When engine sees "type": "ai" in JSON, it looks up NODE_REGISTRY["ai"]
# and gets the AINode class back.
NODE_REGISTRY = {
    "ai":        AINode,
    "scrape":    ScrapeNode,
    "transform": TransformNode,
    "filter":    FilterNode,
    "email":     EmailNode,
}