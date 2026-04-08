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
*   `last_action_error` (str | null): Error from the previous step.

### Action Space
*   `department`: One of `billing`, `support`, `engineering`, `sales`, `none`.
*   `action`: One of `resolve`, `escalate`, `request_info`, `mark_spam`.
*   `confidence`: Float between 0.0 and 1.0.

### Reward Design (0.0 to 1.0)
The environment provides partial progress signals:
*   **+0.6** for choosing the correct department.
*   **+0.3** for choosing the correct action (e.g., escalate vs resolve).
*   **+0.1** for correctly handling high priority SLA escalations.
*   **-0.7** for routing to the incorrect department.
*   **-1.0** for missing a spam mark.

## Tasks & Difficulties
1.  **Easy**: Route standard straightforward emails. No complex threads.
2.  **Medium**: Route ambiguous emails and correctly classify sneaky spam.
3.  **Hard**: Extreme SLAs, angry customers, infrastructure outages, legal threats that strictly require escalation.

## Setup Instructions

1. **Clone Repo**: `git clone <your-repo> && cd email-triage-env`
2. **Install**: `pip install -r requirements.txt`
3. **Validate**: `openenv validate`

## Running Inference (Baseline)
You need to pass in your OpenAI / OpenRouter token.
```bash
export OPENAI_API_KEY="sk-..."
python inference.py
```

## Running Docker
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 -it email-triage-env
```
