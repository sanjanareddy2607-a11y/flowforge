# engine/state_manager.py

# WHAT THIS DOES:
# Keeps track of what's happening during a workflow run.
# Saves results from each node so later nodes can access them.
# Persists the run history to a JSON file so you can view past runs.

# WHY STATE MANAGEMENT MATTERS:
# In multi-step pipelines, each step needs the previous step's output.
# State management is how data flows between steps without using global variables.

import json
import os
from datetime import datetime

# Path where run history is saved
RUNS_FILE = "db/runs.json"

class StateManager:
    """
    Manages workflow run state and persists run history.
    
    During a run, state looks like:
    {
        "run_id": "run_20240115_143022",
        "workflow": "competitor_monitor",
        "status": "running",  # or "completed" or "failed"
        "started_at": "2024-01-15T14:30:22",
        "nodes": {
            "fetch_news": {
                "status": "completed",
                "output": {"raw_text": "..."},
                "completed_at": "2024-01-15T14:30:25"
            },
            ...
        },
        "final_output": {...}
    }
    """

    def __init__(self, workflow_name: str):
        # Create a unique run ID using the current timestamp
        timestamp     = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id   = f"run_{timestamp}"
        self.workflow = workflow_name

        # Initialize the state dictionary
        self.state = {
            "run_id":     self.run_id,
            "workflow":   workflow_name,
            "status":     "running",
            "started_at": datetime.now().isoformat(),
            "nodes":      {},
            "final_output": None
        }

    def update_node_status(self, node_id: str, status: str, output: dict = None):
        """
        Called after each node runs to record what happened.
        status = "running", "completed", or "failed"
        """
        self.state["nodes"][node_id] = {
            "status":       status,
            "output":       output or {},
            "completed_at": datetime.now().isoformat()
        }

    def set_final_output(self, output: dict):
        """Called when the entire workflow completes."""
        self.state["final_output"] = output
        self.state["status"]       = "completed"
        self.state["completed_at"] = datetime.now().isoformat()

    def set_failed(self, reason: str):
        """Called if the workflow fails."""
        self.state["status"]      = "failed"
        self.state["fail_reason"] = reason

    def get_state(self) -> dict:
        """Returns the current state dict (used by /status endpoint)."""
        return self.state

    def save_to_disk(self):
        """
        Saves this run's state to db/runs.json.
        This creates the run history you see in the dashboard.
        """
        # Make sure the db folder exists
        os.makedirs("db", exist_ok=True)

        # Load existing runs (or start with empty list)
        existing_runs = []
        if os.path.exists(RUNS_FILE):
            with open(RUNS_FILE, "r") as f:
                try:
                    existing_runs = json.load(f)
                except:
                    existing_runs = []

        # Add this run to history
        existing_runs.append(self.state)

        # Save back to file
        with open(RUNS_FILE, "w") as f:
            json.dump(existing_runs, f, indent=2)