
import numpy as np
import pandas as pd

def compute_fatigue(events: pd.DataFrame, window_days: int = 7, threshold: int = 4):
    """Return per-contact weekly touch counts and a fatigue flag."""
    if events.empty:
        return pd.DataFrame(columns=["contact_id","touches","fatigue_flag"])
    df = events.copy()
    max_dt = df["event_dt"].max()
    window_start = max_dt - pd.Timedelta(days=window_days)
    recent = df[df["event_dt"] >= window_start]
    touches = recent.groupby("contact_id").size().rename("touches").reset_index()
    touches["fatigue_flag"] = touches["touches"] > threshold
    return touches

def engagement_score(events: pd.DataFrame):
    """Assign a 0-100 score based on last 28 days behavior by persona & channel."""
    if events.empty:
        return pd.DataFrame(columns=["contact_id","engagement_score"])
    df = events.copy()
    cutoff = df["event_dt"].max() - pd.Timedelta(days=28)
    recent = df[df["event_dt"] >= cutoff]
    agg = recent.groupby("contact_id").agg({
        "opened":"mean",
        "clicked":"mean",
        "unsubscribed":"mean"
    }).fillna(0.0).reset_index()
    agg["engagement_score"] = (
        40*agg["opened"] + 70*agg["clicked"] - 100*agg["unsubscribed"]
    ).clip(lower=0)
    return agg[["contact_id","engagement_score"]]

TEMPLATES = [
    "{persona}, unlock faster {benefit}",
    "New: Make {benefit} happen today",
    "A smarter path to {benefit}",
    "Quick win for {persona}: {benefit}",
    "Because you value {benefit}",
]

BENEFITS = ["workflows", "savings", "onboarding", "insights", "decisions", "automation"]

def suggest_subject_lines(persona: str, n: int = 5, seed: int = 0):
    rng = np.random.default_rng(seed)
    picks = []
    for _ in range(n):
        tpl = rng.choice(TEMPLATES)
        ben = rng.choice(BENEFITS)
        picks.append(tpl.format(persona=persona, benefit=ben))
    return picks

def simulate_ai_uplift(metrics: dict, uplift: float = 0.08):
    """Return a new metrics dict with AI-on uplift applied to opens/clicks."""
    m = metrics.copy()
    for key in ["open_rate","ctr","ctor"]:
        if key in m and m[key] is not None:
            m[key] = round(m[key] * (1.0 + uplift), 4)
    return m
