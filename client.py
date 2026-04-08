from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from typing import Dict

from src.models import EmailAction, EmailObservation

class EmailTriageEnvClient(EnvClient[EmailAction, EmailObservation, State]):
    def _step_payload(self, action: EmailAction) -> Dict:
        # Cross-version pydantic support
        try:
            return action.model_dump()
        except:
            return action.dict()

    def _parse_result(self, payload: Dict) -> StepResult[EmailObservation]:
        obs_data = payload.get("observation", {})
        observation = EmailObservation(**obs_data)
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id", "default"),
            step_count=payload.get("step_count", 0),
        )
