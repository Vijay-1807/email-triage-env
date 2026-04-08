import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI

from src.env import EmailTriageEnv
from src.models import EmailAction

# ─── Configuration ───────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = HF_TOKEN or OPENAI_API_KEY or "dummy"

MAX_STEPS = 8
TEMPERATURE = 0.0

SYSTEM_PROMPT = textwrap.dedent("""
    You are a customer support triage agent.
    Based on the priority, SLA, and email thread, output a JSON object with:
    - department: one of ["billing", "support", "engineering", "sales", "none"]
    - action: one of ["resolve", "escalate", "request_info", "mark_spam"]
    - confidence: float between 0.0 and 1.0
    Return *only* the JSON object.
""").strip()


# ─── Mandatory Logging Functions ─────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# ─── Prompt Builder ──────────────────────────────────────────────────────────

def build_user_prompt(obs) -> str:
    thread_text = "\n".join(obs.email_thread)
    return textwrap.dedent(f"""
        Priority: {obs.priority}
        SLA Hours Remaining: {obs.sla_hours_remaining}
        Queue Remaining: {obs.queue_remaining}
        Last Feedback: {obs.last_decision_feedback or 'None'}
        Thread:
        {thread_text}
    """).strip()


# ─── LLM Call ────────────────────────────────────────────────────────────────

def get_model_action(client: OpenAI, obs) -> dict:
    user_prompt = build_user_prompt(obs)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=TEMPERATURE,
            max_tokens=150,
            stream=False,
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")
        return json.loads(content)
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return {"department": "support", "action": "resolve", "confidence": 0.5}


# ─── Main Loop ───────────────────────────────────────────────────────────────

def main():
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    env_name = "email-triage"
    levels = ["easy", "medium", "hard"]

    for level in levels:
        log_start(task=level, env=env_name, model=MODEL_NAME)

        env = EmailTriageEnv(level=level)
        obs = env.reset()

        step_count = 0
        rewards = []

        while not obs.done and step_count < MAX_STEPS:
            step_count += 1
            error_val = None

            try:
                if API_KEY == "dummy":
                    action_data = {"department": "support", "action": "resolve", "confidence": 0.5}
                else:
                    action_data = get_model_action(client, obs)

                action = EmailAction(**action_data)
                action_str = f"dept={action.department}|act={action.action}"

                obs = env.step(action)
                step_reward = obs.reward if obs.reward is not None else 0.01
                # Clamp individual step reward to strict (0, 1)
                step_reward = max(0.01, min(0.99, step_reward))
                done_val = obs.done

            except Exception as e:
                error_val = str(e)
                action_str = "error"
                step_reward = 0.01
                done_val = True

            rewards.append(step_reward)
            log_step(step=step_count, action=action_str, reward=step_reward, done=done_val, error=error_val)

            if done_val:
                break

        # Compute final normalized score in (0, 1)
        final_score = env.normalized_score
        success = final_score > 0.01 and len(rewards) > 0
        log_end(success=success, steps=step_count, score=final_score, rewards=rewards)
        env.close()


if __name__ == "__main__":
    main()
