# Version: 1.0.4-Force-Sync
from typing import Optional
from pydantic import BaseModel

from .models import EmailObservation, EmailAction, EmailReward, EmailState
from .tasks import EmailTaskLoader
from .graders import grade_step

class EnvResult(BaseModel):
    observation: EmailObservation
    reward: float
    done: bool
    info: dict

class EmailTriageEnv:
    """
    OpenEnv compliant Environment for Customer Support Email Triage.
    """
    SUPPORTS_CONCURRENT_SESSIONS = True
    
    def __init__(self, level: str = "easy"):
        self.level = level
        self.loader = EmailTaskLoader(level=level)
        self.current_email = None
        self.total_score = 0.0
        self.last_decision_feedback = None
        self.step_count = 0
        self.episode_id = f"email-triage-{level}-1"
        
    async def reset_async(self):
        return self.reset()

    async def step_async(self, action):
        return self.step(action)
        
    def reset(self) -> EnvResult:
        self.loader.reset()
        self.current_email = self.loader.next_email()
        self.total_score = 0.0
        self.last_decision_feedback = None
        self.step_count = 0
        obs = self._make_obs()
        return EnvResult(observation=obs, reward=0.0, done=False, info={"status": "reset"})
        
    @property
    def state(self) -> EmailState:
        return EmailState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            task_level=self.level,
            current_idx=self.loader.current_index,
            total_emails=self.loader.total(),
            is_done=(self.current_email is None),
            score=self.total_score
        )
        
    def _make_obs(self) -> EmailObservation:
        if not self.current_email:
            return EmailObservation(
                email_thread=["END OF QUEUE"],
                priority="low",
                sla_hours_remaining=0.0,
                queue_remaining=0,
                last_decision_feedback=self.last_decision_feedback
            )
        return EmailObservation(
            email_thread=self.current_email["thread"],
            priority=self.current_email["priority"],
            sla_hours_remaining=self.current_email["sla"],
            queue_remaining=self.loader.remaining(),
            last_decision_feedback=self.last_decision_feedback
        )
        
    def step(self, action: EmailAction) -> EnvResult:
        if not self.current_email:
            self.last_decision_feedback = "Task queue already empty."
            return EnvResult(
                observation=self._make_obs(), 
                reward=0.0, 
                done=True, 
                info={"error": self.last_decision_feedback, "total_score": self.total_score}
            )
            
        self.step_count += 1
        try:
            expected_dept = self.current_email["expected_dept"]
            expected_action = self.current_email["expected_action"]
            
            # Use grading logic
            reward_obj = grade_step(action, expected_dept, expected_action, self.total_score)
            self.total_score = reward_obj.total_score
            step_reward = reward_obj.step_reward
            self.last_decision_feedback = reward_obj.feedback_message
            info = {
                "step_details": reward_obj.details,
                "current_total_score": self.total_score
            }
        except Exception as e:
            self.last_decision_feedback = str(e)
            step_reward = -0.5
            info = {"error": str(e)}

        # Load next email
        self.current_email = self.loader.next_email()
        done = (self.current_email is None)
        obs = self._make_obs()
        
        return EnvResult(observation=obs, reward=step_reward, done=done, info=info)
