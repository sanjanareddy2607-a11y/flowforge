# engine/workflow_runner.py

# WHAT THIS DOES:
# This is the core orchestration engine.
# It reads a workflow JSON file, instantiates each node using the registry,
# runs them in sequence, and passes the output of each node as input to the next.

# THIS IS THE MOST IMPORTANT FILE TO UNDERSTAND FOR INTERVIEWS.
# It demonstrates: pipeline orchestration, the registry pattern,
# state management, error handling, and sequential data flow.

import json
import os
from engine.node_registry  import NODE_REGISTRY
from engine.state_manager  import StateManager

class WorkflowRunner:
    """
    Loads and executes a workflow from a JSON config file.
    
    Usage:
        runner = WorkflowRunner("workflows/competitor_monitor.json")
        result = runner.run()
    """

    def __init__(self, workflow_path: str):
        # Step 1: Load the workflow JSON from disk
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        with open(workflow_path, "r") as f:
            self.workflow = json.load(f)

        # workflow name is used for logging/state management
        self.workflow_name = self.workflow.get("name", "unnamed_workflow")
        self.nodes_config  = self.workflow.get("nodes", [])

        # Initialize state manager for this run
        self.state_manager = StateManager(self.workflow_name)

    def run(self) -> dict:
        """
        Executes the workflow.
        
        How it works:
        1. Start with empty input data (no previous node for the first one)
        2. For each node in order:
           a. Look up the node class in the registry
           b. Create an instance of that class with its config
           c. Call node.run(current_data) → get output
           d. Merge the output into current_data (so ALL previous outputs are available)
           e. Update state manager
        3. Return the final accumulated data
        """
        print(f"\n🚀 Starting workflow: {self.workflow_name}")
        print(f"   Run ID: {self.state_manager.run_id}")
        print(f"   Nodes to run: {len(self.nodes_config)}\n")

        # This accumulates ALL outputs from ALL nodes as we go
        # Each node receives ALL data produced so far — not just the previous node's output
        current_data = {}

        for i, node_config in enumerate(self.nodes_config):
            node_id   = node_config.get("id",     f"node_{i}")
            node_type = node_config.get("type",   "ai")
            config    = node_config.get("config", {})

            print(f"▶ Running node [{i+1}/{len(self.nodes_config)}]: '{node_id}' (type: {node_type})")

            # Step A: Look up the class for this node type
            NodeClass = NODE_REGISTRY.get(node_type)
            if NodeClass is None:
                error_msg = f"Unknown node type: '{node_type}'. Available: {list(NODE_REGISTRY.keys())}"
                print(f"   ❌ Error: {error_msg}")
                self.state_manager.update_node_status(node_id, "failed", {"error": error_msg})
                self.state_manager.set_failed(error_msg)
                self.state_manager.save_to_disk()
                return {"error": error_msg, "run_id": self.state_manager.run_id}

            # Step B: Instantiate the node with its ID and config
            node = NodeClass(node_id=node_id, config=config)

            # Step C: Run the node with accumulated data so far
            try:
                self.state_manager.update_node_status(node_id, "running")
                node_output = node.run(current_data)

                # Step D: Merge this node's output into accumulated data
                # This is why later nodes can access ANY previous node's output
                current_data.update(node_output)

                print(f"   ✅ Completed. Output keys: {list(node_output.keys())}")
                self.state_manager.update_node_status(node_id, "completed", node_output)

                # Step E: Check if a filter node blocked the pipeline
                if node_type == "filter" and not current_data.get("filter_passed", True):
                    msg = f"Pipeline stopped by filter node '{node_id}': {current_data.get('filter_message')}"
                    print(f"\n🛑 {msg}")
                    self.state_manager.set_failed(msg)
                    self.state_manager.save_to_disk()
                    return {"stopped_by_filter": msg, "data": current_data, "run_id": self.state_manager.run_id}

            except Exception as e:
                error_msg = f"Node '{node_id}' crashed: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.state_manager.update_node_status(node_id, "failed", {"error": error_msg})
                self.state_manager.set_failed(error_msg)
                self.state_manager.save_to_disk()
                return {"error": error_msg, "run_id": self.state_manager.run_id}

        # All nodes completed successfully
        print(f"\n✅ Workflow '{self.workflow_name}' completed!")
        self.state_manager.set_final_output(current_data)
        self.state_manager.save_to_disk()

        return {
            "run_id":       self.state_manager.run_id,
            "workflow":     self.workflow_name,
            "status":       "completed",
            "final_output": current_data
        }