

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import json
import os

from engine.workflow_runner import WorkflowRunner

# Initialize FastAPI app
app = FastAPI(
    title="FlowForge",
    description="Multi-Agent AI Workflow Automation Engine",
    version="1.0.0"
)

# In-memory store for active runs
# Key = run_id, Value = state dict
# In production you'd use Redis or a database, but for demo JSON files are fine
active_runs: dict = {}

# ─────────────────────────────────────────────
# Request/Response Models (Pydantic)
# These validate what comes IN and goes OUT of your API
# ─────────────────────────────────────────────

class RunWorkflowRequest(BaseModel):
    workflow_name: str          # e.g. "hn_digest" or "competitor_monitor"
    async_mode: Optional[bool] = False  # if True, runs in background

class RunWorkflowResponse(BaseModel):
    run_id: str
    status: str
    message: str

# ─────────────────────────────────────────────
# Helper function
# ─────────────────────────────────────────────

def run_workflow_sync(workflow_name: str) -> dict:
    """
    Runs a workflow synchronously and stores the result in active_runs.
    Called both directly and as a background task.
    """
    workflow_path = f"workflows/{workflow_name}.json"

    try:
        runner = WorkflowRunner(workflow_path)
        result = runner.run()

        # Store in memory for /status lookups
        run_id = result.get("run_id", "unknown")
        active_runs[run_id] = result

        return result

    except FileNotFoundError:
        return {"error": f"Workflow '{workflow_name}' not found in workflows/ folder"}
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────

@app.get("/")
def serve_dashboard():
    """Serves the HTML dashboard."""
    return FileResponse("static/index.html")


@app.post("/run", response_model=None)
def run_workflow(request: RunWorkflowRequest, background_tasks: BackgroundTasks):
    """
    Triggers a workflow run.
    
    If async_mode=True: starts workflow in background, returns run_id immediately.
    If async_mode=False: waits for completion, returns full result.
    
    Example request body:
        {"workflow_name": "hn_digest"}
    """
    workflow_path = f"workflows/{request.workflow_name}.json"

    if not os.path.exists(workflow_path):
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{request.workflow_name}' not found. Available: {get_available_workflows()}"
        )

    if request.async_mode:
        # Start in background — return immediately with a placeholder run_id
        # The background task will update active_runs when done
        import uuid
        temp_run_id = f"run_pending_{uuid.uuid4().hex[:8]}"
        active_runs[temp_run_id] = {"status": "queued", "run_id": temp_run_id}

        background_tasks.add_task(run_workflow_sync, request.workflow_name)

        return JSONResponse({
            "run_id":  temp_run_id,
            "status":  "queued",
            "message": f"Workflow '{request.workflow_name}' queued. Poll /status/{temp_run_id} for updates."
        })
    else:
        # Synchronous: wait for full result
        result = run_workflow_sync(request.workflow_name)
        return JSONResponse(result)


@app.get("/status/{run_id}")
def get_run_status(run_id: str):
    """
    Returns the state of a specific run.
    
    Checks in-memory first, then falls back to the runs.json file on disk.
    """
    # Check in-memory store first
    if run_id in active_runs:
        return JSONResponse(active_runs[run_id])

    # Check disk history
    runs_file = "db/runs.json"
    if os.path.exists(runs_file):
        with open(runs_file, "r") as f:
            try:
                runs = json.load(f)
                for run in runs:
                    if run.get("run_id") == run_id:
                        return JSONResponse(run)
            except:
                pass

    raise HTTPException(status_code=404, detail=f"Run ID '{run_id}' not found.")


@app.get("/workflows")
def list_workflows():
    """Lists all available workflow JSON files in the workflows/ folder."""
    workflows_dir = "workflows"
    if not os.path.exists(workflows_dir):
        return JSONResponse({"workflows": []})

    workflow_files = [
        f.replace(".json", "")
        for f in os.listdir(workflows_dir)
        if f.endswith(".json")
    ]

    # Load each workflow to get its description too
    workflows_info = []
    for wf_name in workflow_files:
        path = f"{workflows_dir}/{wf_name}.json"
        with open(path, "r") as f:
            data = json.load(f)
        workflows_info.append({
            "name":        wf_name,
            "description": data.get("description", ""),
            "num_nodes":   len(data.get("nodes", []))
        })

    return JSONResponse({"workflows": workflows_info})


@app.get("/history")
def get_run_history():
    """Returns all past workflow runs from db/runs.json."""
    runs_file = "db/runs.json"
    if not os.path.exists(runs_file):
        return JSONResponse({"runs": [], "total": 0})

    with open(runs_file, "r") as f:
        try:
            runs = json.load(f)
        except:
            runs = []

    return JSONResponse({"runs": runs, "total": len(runs)})


def get_available_workflows():
    """Helper to get list of workflow names (used in error messages)."""
    if not os.path.exists("workflows"):
        return []
    return [f.replace(".json", "") for f in os.listdir("workflows") if f.endswith(".json")]

