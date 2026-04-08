# Version: 2.0.0 — Full OpenEnv Spec Compliance
from typing import Optional, Any

from .models import EmailObservation, EmailAction, EmailReward, EmailState
from .tasks import EmailTaskLoader
from .graders import grade_step


class EmailTriageEnv:
    """
    OpenEnv-compliant Environment for Customer Support Email Triage.

    reset() -> EmailObservation (with done=False, reward=None)
    step(action) -> EmailObservation (with done, reward fields set)
    state (property) -> EmailState
    close() -> None
    """
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self, level: str = "easy"):
        self.level = level
        self.loader = EmailTaskLoader(level=level)
        self.current_email = None
        self.total_score = 0.0
        self.last_decision_feedback = None
        self._step_count = 0
        self._episode_id = f"email-triage-{level}-1"

    def close(self) -> None:
        """Clean up resources. Required by OpenEnv framework."""
        pass

    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs) -> EmailObservation:
        """Reset the environment and return initial observation."""
        self.loader.reset()
        self.current_email = self.loader.next_email()
        self.total_score = 0.0
        self.last_decision_feedback = None
        self._step_count = 0
        if episode_id:
            self._episode_id = episode_id
        return self._make_obs(reward=None, done=False)

    async def reset_async(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs) -> EmailObservation:
        return self.reset(seed=seed, episode_id=episode_id, **kwargs)

    def step(self, action: EmailAction, timeout_s: Optional[float] = None, **kwargs) -> EmailObservation:
        """Take a step in the environment."""
        if not self.current_email:
            self.last_decision_feedback = "Task queue already empty."
            return self._make_obs(reward=0.0, done=True)

        self._step_count += 1
        try:
            expected_dept = self.current_email["expected_dept"]
            expected_action = self.current_email["expected_action"]

            reward_obj = grade_step(action, expected_dept, expected_action, self.total_score)
            self.total_score = reward_obj.total_score
            step_reward = reward_obj.step_reward
            self.last_decision_feedback = reward_obj.feedback_message
        except Exception as e:
            self.last_decision_feedback = str(e)
            step_reward = 0.0

        # Load next email
        self.current_email = self.loader.next_email()
        done = (self.current_email is None)

        return self._make_obs(reward=step_reward, done=done)

    async def step_async(self, action: EmailAction, timeout_s: Optional[float] = None, **kwargs) -> EmailObservation:
        return self.step(action, timeout_s=timeout_s, **kwargs)

    @property
    def state(self) -> EmailState:
        """Get the current environment state."""
        return EmailState(
            episode_id=self._episode_id,
            step_count=self._step_count,
            task_level=self.level,
            current_idx=self.loader.current_index,
            total_emails=self.loader.total(),
            is_done=(self.current_email is None),
            score=self.total_score
        )

    def _make_obs(self, reward: Optional[float], done: bool) -> EmailObservation:
        """Build an EmailObservation with OpenEnv-required done/reward fields."""
        if not self.current_email:
            return EmailObservation(
                email_thread=["END OF QUEUE"],
                priority="low",
                sla_hours_remaining=0.0,
                queue_remaining=0,
                last_decision_feedback=self.last_decision_feedback,
                done=done,
                reward=reward,
            )
        return EmailObservation(
            email_thread=self.current_email["thread"],
            priority=self.current_email["priority"],
            sla_hours_remaining=self.current_email["sla"],
            queue_remaining=self.loader.remaining(),
            last_decision_feedback=self.last_decision_feedback,
            done=done,
            reward=reward,
        )
