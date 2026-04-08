from pydantic import Field
from typing import List, Literal, Optional, Dict, Any

from openenv.core.env_server.types import Action, Observation, State


class EmailObservation(Observation):
    """Observation returned by the Email Triage environment."""
    email_thread: List[str] = Field(..., description="Full conversation history between user and support.")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority level of the ticket.")
    sla_hours_remaining: float = Field(..., description="Time remaining in hours to meet the Service Level Agreement.")
    queue_remaining: int = Field(..., description="Number of emails left in the current task queue.")
    last_decision_feedback: Optional[str] = Field(None, description="Detailed feedback explaining why the previous decision was correct or incorrect.")


class EmailAction(Action):
    """Action taken by the agent in the Email Triage environment."""
    department: Literal["billing", "support", "engineering", "sales", "none"] = Field(..., description="The department to route this ticket to. Use 'none' if marking spam or resolving directly.")
    action: Literal["resolve", "escalate", "request_info", "mark_spam"] = Field(..., description="The core action to take on this thread.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")


class EmailReward(Observation):
    """Internal reward tracking model (not returned directly)."""
    step_reward: float = Field(..., description="Reward gained in this step (0.0 to 1.0).")
    total_score: float = Field(..., description="Cumulative score for the episode.")
    details: str = Field(..., description="Breakdown of the reward (e.g., +0.6 for dept, +0.3 for action).")
    feedback_message: str = Field(..., description="Clear feedback message passed to the next observation.")


class EmailState(State):
    """State of the Email Triage environment."""
    task_level: str = Field(..., description="Current difficulty level (easy, medium, hard).")
    current_idx: int = Field(..., description="Index of the current email.")
    total_emails: int = Field(..., description="Total emails in this episode queue.")
    is_done: bool = Field(..., description="Whether the episode is finished.")
    score: float = Field(0.0, description="Current internal score.")
