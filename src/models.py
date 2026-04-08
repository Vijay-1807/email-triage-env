from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class EmailObservation(BaseModel):
    email_thread: List[str] = Field(..., description="Full conversation history between user and support.")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority level of the ticket.")
    sla_hours_remaining: float = Field(..., description="Time remaining in hours to meet the Service Level Agreement.")
    queue_remaining: int = Field(..., description="Number of emails left in the current task queue.")
    last_decision_feedback: Optional[str] = Field(None, description="Detailed feedback explaining why the previous decision was correct or incorrect.")

class EmailAction(BaseModel):
    department: Literal["billing", "support", "engineering", "sales", "none"] = Field(..., description="The department to route this ticket to. Use 'none' if marking spam or resolving directly.")
    action: Literal["resolve", "escalate", "request_info", "mark_spam"] = Field(..., description="The core action to take on this thread.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")

class EmailReward(BaseModel):
    step_reward: float = Field(..., description="Reward gained in this step (-1.0 to 1.0).")
    total_score: float = Field(..., description="Cumulative score for the episode.")
    details: str = Field(..., description="Breakdown of the reward (e.g., +0.6 for dept, +0.3 for action).")
    feedback_message: str = Field(..., description="Clear feedback message passed to the next observation.")

class EmailState(BaseModel):
    episode_id: str = Field("email-episode", description="Unique episode ID required by OpenEnv.")
    step_count: int = Field(0, description="Step count required by OpenEnv.")
    task_level: str = Field(..., description="Current difficulty level (easy, medium, hard).")
    current_idx: int = Field(..., description="Index of the current email.")
    total_emails: int = Field(..., description="Total emails in this episode queue.")
    is_done: bool = Field(..., description="Whether the episode is finished.")
    score: float = Field(0.0, description="Current internal score.")
