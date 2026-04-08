EASY_TASKS = [
    {
        "id": "e1",
        "thread": ["User: Can you send me the invoice for last month? I need it for accounting."],
        "priority": "low",
        "sla": 48.0,
        "expected_dept": "billing",
        "expected_action": "resolve"
    },
    {
        "id": "e2",
        "thread": ["User: I want to talk to sales about a custom enterprise plan."],
        "priority": "medium",
        "sla": 24.0,
        "expected_dept": "sales",
        "expected_action": "resolve"
    },
    {
        "id": "e3",
        "thread": ["User: My API is returning a 500 internal server error."],
        "priority": "high",
        "sla": 4.0,
        "expected_dept": "engineering",
        "expected_action": "escalate"
    }
]

MEDIUM_TASKS = [
    {
        "id": "m1",
        "thread": [
            "User: Hi, are there any discounts?",
            "Agent: Yes, we have a 10% discount for students.",
            "User: I'm not a student, but what if I buy 50 seats?"
        ],
        "priority": "medium",
        "sla": 12.0,
        "expected_dept": "sales",
        "expected_action": "escalate" # because it's bulk
    },
    {
        "id": "m2",
        "thread": ["Earn $5k a week working from home!!! Click here -> bit.ly/spam"],
        "priority": "low",
        "sla": 72.0,
        "expected_dept": "none",
        "expected_action": "mark_spam"
    },
    {
        "id": "m3",
        "thread": [
            "User: I tried logging in but it says account blocked.",
            "Agent: Let me check. Can you confirm your email?",
            "User: Yes, it is test@example.com."
        ],
        "priority": "medium",
        "sla": 12.0,
        "expected_dept": "support",
        "expected_action": "resolve"
    }
]

HARD_TASKS = [
    {
        "id": "h1",
        "thread": [
            "User: It's been 5 days and I haven't received my refund!!",
            "Agent: We processed it on our end. It might take 3-5 business days.",
            "User: I am filing a chargeback and a BBB complaint tomorrow if this isn't resolved now!"
        ],
        "priority": "high",
        "sla": 1.0,
        "expected_dept": "billing",
        "expected_action": "escalate" 
    },
    {
        "id": "h2",
        "thread": [
            "User: The new staging deployment broke our prod environment. We are losing $10k an hour.",
            "Agent: Checking the logs now.",
            "User: The database cluster went completely offline after the 3.2.1 migration."
        ],
        "priority": "high",
        "sla": 0.5,
        "expected_dept": "engineering",
        "expected_action": "escalate"
    },
    {
        "id": "h3",
        "thread": [
            "User: Hello, I have an amazing SEO proposal for your website...",
            "Agent: Not interested.",
            "User: Wait! Don't you want 10x traffic? I can hook you up with totally legit backlinks."
        ],
        "priority": "low",
        "sla": 24.0,
        "expected_dept": "none",
        "expected_action": "mark_spam"
    }
]

# Provide a dictionary mapping task level to dataset
DATASETS = {
    "easy": EASY_TASKS,
    "medium": MEDIUM_TASKS,
    "hard": HARD_TASKS
}
