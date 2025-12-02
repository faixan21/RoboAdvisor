# modules/goals.py

from dataclasses import dataclass
from math import pow

@dataclass
class Goal:
    name: str
    target_amount: float      # how much money you need
    years: int                # in how many years
    expected_return: float    # expected annual return in %
    risk_profile: str | None = None


def sip_required(goal: Goal) -> float:
    """
    Calculate required monthly SIP amount
    using future value of annuity formula.
    """
    r = goal.expected_return / 100 / 12        # monthly rate
    n = goal.years * 12                        # months

    if r == 0:
        return goal.target_amount / n

    factor = (pow(1 + r, n) - 1) / r
    monthly = goal.target_amount / factor
    return monthly


def describe_goal_plan(goal: Goal) -> str:
    monthly = sip_required(goal)
    text = [
        f"Goal: {goal.name}",
        f"Target Amount: ₹{goal.target_amount:,.0f}",
        f"Time Horizon: {goal.years} years",
        f"Assumed Return: {goal.expected_return:.1f}% p.a.",
        f"Approx. SIP Required: ₹{monthly:,.0f} per month",
    ]
    if goal.risk_profile:
        text.append(f"Risk Profile: {goal.risk_profile}")
    return "\n".join(text)