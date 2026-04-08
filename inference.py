import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI

from src.env import EmailTriageEnv
from src.models import EmailAction

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

def main():
    # Credentials and endpoints
    hf_token = os.getenv("HF_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    api_key = hf_token or openai_key or "dummy"
    
    base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1") 
    model_name = os.getenv("MODEL_NAME", "gpt-4")
    env_name = "email-triage"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
    except Exception as e:
        print(f"Failed to init OpenAI client: {e}")
        return

    levels = ["easy", "medium", "hard"]
    
    for level in levels:
        log_start(task=level, env=env_name, model=model_name)
        
        env = EmailTriageEnv(level=level)
        reset_res = env.reset()
        obs = reset_res.observation
        
        step_count = 0
        rewards = []
        
        while True:
            # We use env.state to check if done initially
            state = env.state
            if state.is_done:
                success = env.total_score > 0 and len(rewards) > 0
                log_end(success=success, steps=step_count, score=env.total_score, rewards=rewards)
                break
                
            step_count += 1
            system_prompt = textwrap.dedent("""
                You are a customer support triage agent. 
                Based on the priority, SLA, and email thread, output a JSON object with:
                - department: one of ["billing", "support", "engineering", "sales", "none"]
                - action: one of ["resolve", "escalate", "request_info", "mark_spam"]
                - confidence: float between 0.0 and 1.0
                Return *only* the JSON object.
            """).strip()
            
            user_msg = textwrap.dedent(f"""
                Priority: {obs.priority}
                SLA Hours Remaining: {obs.sla_hours_remaining}
                Queue Remaining: {obs.queue_remaining}
                Last Error feedback: {obs.last_decision_feedback or 'None'}
                Thread:
                { chr(10).join(obs.email_thread) }
            """).strip()

            action_str = ""
            error_val = None
            step_reward = 0.0
            done_val = False

            try:
                if api_key == "dummy":
                    action_data = {"department": "support", "action": "resolve", "confidence": 0.5}
                else:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt}, 
                            {"role": "user", "content": user_msg}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.0
                    )
                    content = response.choices[0].message.content
                    if not content:
                        raise ValueError("Empty response from LLM")
                    action_data = json.loads(content)
                
                action = EmailAction(**action_data)
                action_str = f"dept={action.department}|act={action.action}"
                
                result = env.step(action)
                obs = result.observation
                step_reward = result.reward
                done_val = result.done
                
            except Exception as e:
                error_val = str(e)
                action_str = "error"
                step_reward = -0.5
                done_val = True
                
            rewards.append(step_reward)
            log_step(step=step_count, action=action_str, reward=step_reward, done=done_val, error=error_val)
            
            if done_val and not state.is_done: # Break early if exception caused done
                 log_end(success=False, steps=step_count, score=env.total_score, rewards=rewards)
                 break

if __name__ == "__main__":
    main()
