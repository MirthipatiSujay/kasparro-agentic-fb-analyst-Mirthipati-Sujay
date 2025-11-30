# src/agents/insight_agent.py

import pandas as pd

def _split_recent_prev(daily: pd.DataFrame, window: int = 7):
    daily_sorted = daily.sort_values("date")
    if len(daily_sorted) < window * 2:
        recent = daily_sorted.tail(window)
        prev = daily_sorted.head(max(0, len(daily_sorted) - window))
    else:
        recent = daily_sorted.tail(window)
        prev = daily_sorted.tail(window * 2).head(window)
    return recent, prev

def generate_hypotheses(summaries):
    """
    Generate deeper hypotheses:
    - ROAS movement
    - CTR movement (possible audience fatigue)
    - CVR movement (conversion rate)
    - Frequency / exposure pressure (impressions vs clicks)
    """
    daily = summaries["daily"]
    recent, prev = _split_recent_prev(daily)

    hypotheses = []

    def pct_change(new, old):
        if old == 0:
            return 0.0
        return (new - old) / old

    recent_roas = recent["roas"].mean()
    prev_roas = prev["roas"].mean() if len(prev) > 0 else recent_roas
    roas_change = pct_change(recent_roas, prev_roas)

    recent_ctr = recent["ctr"].mean()
    prev_ctr = prev["ctr"].mean() if len(prev) > 0 else recent_ctr
    ctr_change = pct_change(recent_ctr, prev_ctr)

    # Conversion rate (CVR = purchases / clicks)
    recent_cvr = (recent["purchases"].sum() / recent["clicks"].sum()) if recent["clicks"].sum() > 0 else 0
    prev_cvr = (prev["purchases"].sum() / prev["clicks"].sum()) if len(prev) > 0 and prev["clicks"].sum() > 0 else recent_cvr
    cvr_change = pct_change(recent_cvr, prev_cvr)

    # "Frequency creep" proxy: more impressions but fewer clicks
    recent_impr = recent["impressions"].sum()
    prev_impr = prev["impressions"].sum() if len(prev) > 0 else recent_impr
    recent_clicks = recent["clicks"].sum()
    prev_clicks = prev["clicks"].sum() if len(prev) > 0 else recent_clicks

    # Base ROAS hypothesis
    if roas_change < -0.05:
        hypotheses.append({
            "hypothesis": "ROAS dropped in the most recent period.",
            "metric": "roas",
            "recent_mean": float(recent_roas),
            "previous_mean": float(prev_roas),
            "relative_change": float(roas_change),
            "driver": "efficiency"
        })
    elif roas_change > 0.05:
        hypotheses.append({
            "hypothesis": "ROAS improved in the most recent period.",
            "metric": "roas",
            "recent_mean": float(recent_roas),
            "previous_mean": float(prev_roas),
            "relative_change": float(roas_change),
            "driver": "efficiency"
        })

    # Audience fatigue / CTR drop
    if ctr_change < -0.05:
        hypotheses.append({
            "hypothesis": "CTR dropped, suggesting possible audience fatigue or creative exhaustion.",
            "metric": "ctr",
            "recent_mean": float(recent_ctr),
            "previous_mean": float(prev_ctr),
            "relative_change": float(ctr_change),
            "driver": "audience_fatigue"
        })

    # Conversion rate dips
    if cvr_change < -0.05:
        hypotheses.append({
            "hypothesis": "Conversion rate (CVR) declined, even if clicks were stable.",
            "metric": "cvr",
            "recent_mean": float(recent_cvr),
            "previous_mean": float(prev_cvr),
            "relative_change": float(cvr_change),
            "driver": "conversion_drop"
        })

    # Frequency / exposure pressure
    if recent_impr > prev_impr and recent_clicks <= prev_clicks:
        hypotheses.append({
            "hypothesis": "Impressions increased but clicks did not, indicating frequency creep or weaker audiences.",
            "metric": "frequency_proxy",
            "recent_impressions": int(recent_impr),
            "previous_impressions": int(prev_impr),
            "recent_clicks": int(recent_clicks),
            "previous_clicks": int(prev_clicks),
            "driver": "frequency_creep"
        })

    # Fallback if nothing interesting
    if not hypotheses:
        hypotheses.append({
            "hypothesis": "No major performance shift detected; ROAS and CTR are relatively stable.",
            "metric": "stability",
            "recent_mean": float(recent_roas),
            "previous_mean": float(prev_roas),
            "relative_change": float(roas_change),
            "driver": "stable"
        })

    return hypotheses
