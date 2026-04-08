---
title: Email Triage Agent
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# OpenEnv: Customer Support Email Triage

This is a real-world OpenEnv environment for **Customer Support Email Triage**.

## Motivation 
Customer support triage is a massive operational cost for companies. This environment trains and evaluates AI agents on their ability to autonomously read customer email threads, respect Service Level Agreements (SLAs), prioritize appropriately, and route tickets to the correct departments or take specific actions (like escalation or marking spam).

## Spaces and Datatypes (Pydantic Models)

### Observation Space
The agent receives a complex observation composed of:
*   `email_thread` (List[str]): The conversation history.
*   `priority` (low/medium/high): The ticket priority.
*   `sla_hours_remaining` (float): Time left before the SLA is breached.
*   `queue_remaining` (int): Number of emails left in the queue.
*   `last_decision_feedback` (str | null): Feedback from the previous step.
*   `done` (bool): Whether the episode is finished.
*   `reward` (float | null): Reward from the last action.

### Action Space
*   `department`: One of `billing`, `support`, `engineering`, `sales`, `none`.
*   `action`: One of `resolve`, `escalate`, `request_info`, `mark_spam`.
*   `confidence`: Float between 0.0 and 1.0.

### Reward Design (0.0 to 1.0)
The environment provides partial progress signals:
*   **+0.6** for choosing the correct department.
*   **+0.3** for choosing the correct action (e.g., escalate vs resolve).
*   **+0.1** for correctly handling high priority SLA escalations.
*   **+0.1 × confidence** bonus for perfect decisions.
*   **-0.7** for routing to the incorrect department.
*   **-1.0** for missing a spam mark.

## Tasks & Difficulties
1.  **Easy** (3 tasks): Route standard straightforward emails. No complex threads. Clear department signals.
2.  **Medium** (3 tasks): Route ambiguous emails, correctly classify sneaky spam, handle multi-turn threads.
3.  **Hard** (3 tasks): Extreme SLAs, angry customers, infrastructure outages, legal threats that strictly require escalation.

## Baseline Scores
With the dummy fallback agent (always picks `support` / `resolve`):
```
[easy]   score=0.000  (3 steps — misses billing, sales, engineering routing)
[medium] score=1.000  (3 steps — gets 1/3 correct: support/resolve)
[hard]   score=0.000  (3 steps — misses billing escalation, engineering escalation, spam)
```

## Setup Instructions

1. **Clone Repo**: `git clone https://github.com/Vijay-1807/email-triage-env && cd email-triage-env`
2. **Install**: `pip install -r requirements.txt`
3. **Validate**: `openenv validate`

## Running Inference (Baseline)
```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4"
export OPENAI_API_KEY="sk-..."
python inference.py
```

## Running Docker
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 -it email-triage-env
```

## Environment Variables
| Variable | Description |
|---|---|
| `API_BASE_URL` | The API endpoint for the LLM (default: `https://api.openai.com/v1`) |
| `MODEL_NAME` | The model identifier (default: `gpt-4`) |
| `HF_TOKEN` | Your Hugging Face / API key |
| `OPENAI_API_KEY` | Your OpenAI API key (fallback if HF_TOKEN not set) |
