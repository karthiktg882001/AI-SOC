"""
SOAR Automation Service
Security Orchestration, Automation, and Response
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

app = FastAPI(title="SOAR Automation Service", version="1.0.0")

class AutomationAction(BaseModel):
    action_type: str  # block_ip, quarantine_file, terminate_process, etc.
    target: str
    incident_id: Optional[str] = None
    severity: Optional[str] = None
    requires_approval: bool = True

class ApprovalRequest(BaseModel):
    action_id: str
    approved: bool
    approver_id: str
    notes: Optional[str] = None

# In-memory storage (in production, use database)
action_history = []
pending_approvals = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "automation-service"}

@app.post("/api/automation/block-ip")
async def block_ip(action: AutomationAction):
    """
    Block an IP address (requires approval for medium/low confidence)
    """
    if action.action_type != "block_ip":
        raise HTTPException(status_code=400, detail="Invalid action type")
    
    action_id = f"block_ip_{datetime.now().timestamp()}"
    
    # High confidence (>0.9) or CRITICAL severity: auto-execute
    auto_execute = (
        action.severity == "CRITICAL" or
        (action.severity == "HIGH" and not action.requires_approval)
    )
    
    if auto_execute:
        # Execute immediately
        result = {
            "action_id": action_id,
            "status": "executed",
            "target": action.target,
            "executed_at": datetime.now().isoformat(),
            "method": "auto"
        }
        action_history.append(result)
        return result
    else:
        # Require approval
        pending_approvals[action_id] = {
            "action": action.dict(),
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        return {
            "action_id": action_id,
            "status": "pending_approval",
            "message": "Action requires approval"
        }

@app.post("/api/automation/quarantine-file")
async def quarantine_file(action: AutomationAction):
    """
    Quarantine a file (always requires approval for safety)
    """
    if action.action_type != "quarantine_file":
        raise HTTPException(status_code=400, detail="Invalid action type")
    
    action_id = f"quarantine_{datetime.now().timestamp()}"
    
    # File quarantine always requires approval
    pending_approvals[action_id] = {
        "action": action.dict(),
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    return {
        "action_id": action_id,
        "status": "pending_approval",
        "message": "File quarantine requires approval"
    }

@app.post("/api/automation/approve")
async def approve_action(approval: ApprovalRequest):
    """
    Approve or reject a pending automation action
    """
    if approval.action_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action_data = pending_approvals[approval.action_id]
    
    if approval.approved:
        # Execute the action
        result = {
            "action_id": approval.action_id,
            "status": "executed",
            "target": action_data["action"]["target"],
            "executed_at": datetime.now().isoformat(),
            "method": "manual_approval",
            "approver": approval.approver_id,
            "notes": approval.notes
        }
        action_history.append(result)
        del pending_approvals[approval.action_id]
        return result
    else:
        # Reject the action
        action_data["status"] = "rejected"
        action_data["rejected_by"] = approval.approver_id
        action_data["rejected_at"] = datetime.now().isoformat()
        action_data["rejection_notes"] = approval.notes
        del pending_approvals[approval.action_id]
        return {
            "action_id": approval.action_id,
            "status": "rejected",
            "message": "Action rejected"
        }

@app.get("/api/automation/history")
async def get_history(limit: int = 50):
    """Get automation action history"""
    return {
        "actions": action_history[-limit:],
        "total": len(action_history)
    }

@app.get("/api/automation/pending")
async def get_pending():
    """Get pending approval requests"""
    return {
        "pending": list(pending_approvals.values()),
        "count": len(pending_approvals)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

