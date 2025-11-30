
def _score_change(rel_change: float, strong_drop: float = -0.2, mild_drop: float = -0.05,
                  strong_gain: float = 0.2, mild_gain: float = 0.05):
    """
    Simple scoring for relative changes.
    Negative values = decline, positive = improvement.
    """
    if rel_change <= strong_drop:
        return 0.9
    if rel_change <= mild_drop:
        return 0.65
    if rel_change >= strong_gain:
        return 0.85
    if rel_change >= mild_gain:
        return 0.6
    return 0.3  # small/no change

def evaluate_hypotheses(hypotheses, summaries, thresholds):
    """
    Attach confidence scores and structured evidence to each hypothesis.
    """
    results = []
    for h in hypotheses:
        metric = h.get("metric")
        driver = h.get("driver", "unknown")
        rel = h.get("relative_change", 0.0)
        confidence = 0.4  # baseline

        evidence = []

        if metric in ("roas", "ctr", "cvr"):
            confidence = _score_change(rel)
            evidence.append(f"{metric} relative_change={rel:.2%}")

        if metric == "frequency_proxy":
            recent_impr = h.get("recent_impressions", 0)
            prev_impr = h.get("previous_impressions", 0)
            recent_clicks = h.get("recent_clicks", 0)
            prev_clicks = h.get("previous_clicks", 0)
            # If impressions up a lot and clicks flat/down => stronger signal
            if prev_impr > 0:
                impr_change = (recent_impr - prev_impr) / prev_impr
            else:
                impr_change = 0.0
            if prev_clicks > 0:
                click_change = (recent_clicks - prev_clicks) / prev_clicks
            else:
                click_change = 0.0

            confidence = max(confidence, _score_change(impr_change))
            evidence.append(f"impressions relative_change={impr_change:.2%}")
            evidence.append(f"clicks relative_change={click_change:.2%}")

        # Map numeric score to label
        label = "low"
        if confidence >= thresholds["high"]:
            label = "high"
        elif confidence >= thresholds["medium"]:
            label = "medium"

        results.append({
            "hypothesis": h["hypothesis"],
            "metric": metric,
            "driver": driver,
            "confidence_score": float(confidence),
            "confidence_label": label,
            "evidence": evidence
        })

    return results
