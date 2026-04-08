from .models import EmailAction, EmailReward


def grade_step(action: EmailAction, expected_dept: str, expected_action: str, current_total_score: float) -> EmailReward:
    score = 0.0
    details = []
    feedback_parts = []

    # Department Scoring
    dept_correct = action.department == expected_dept
    if dept_correct:
        score += 0.6
        details.append("+0.6 correct dept")
        feedback_parts.append("Department correct.")
    else:
        if expected_action == "mark_spam":
            score -= 1.0
            details.append("-1.0 spam misclassified")
            feedback_parts.append("CRITICAL: Missed spam classification.")
        else:
            score -= 0.7
            details.append(f"-0.7 wrong dept (expected {expected_dept})")
            feedback_parts.append(f"Wrong department: should be {expected_dept}.")

    # Action Scoring
    action_correct = action.action == expected_action
    if action_correct:
        score += 0.3
        details.append("+0.3 correct action")
        feedback_parts.append("Action correct.")
    else:
        score -= 0.3
        details.append(f"-0.3 wrong action (expected {expected_action})")
        feedback_parts.append(f"Wrong action: should be {expected_action}.")

    # Priority / SLA Bonus
    if action_correct:
        score += 0.1
        if expected_action == "escalate":
            details.append("+0.1 correct priority handling (escalated)")
        else:
            details.append("+0.1 correct priority handling")

    # Confidence Calibration Bonus
    if dept_correct and action_correct:
        conf_bonus = 0.1 * action.confidence
        score += conf_bonus
        details.append(f"+{conf_bonus:.2f} confidence bonus")
        feedback_parts.append(f"Perfect decision with {action.confidence*100:.0f}% confidence!")

    # Clamp to strict open interval (0, 1) — evaluator rejects exactly 0.0 and 1.0
    step_reward = max(0.01, min(0.99, score))
    new_total = current_total_score + step_reward

    return EmailReward(
        step_reward=step_reward,
        total_score=new_total,
        details=", ".join(details),
        feedback_message=" ".join(feedback_parts),
        done=False,
        reward=step_reward,
    )
