import numpy as np
def evaluate_hypotheses(hypotheses, summaries, thresholds):
    results = []
    for h in hypotheses:
        confidence = 0.0
        evidence = []
        # simple rules
        if h['metric']=='roas':
            change = h['relative_change']
            if change <= -0.2:
                confidence = 0.9
            elif change <= -0.05:
                confidence = 0.65
            else:
                confidence = 0.2
            evidence.append(f"roas change {change:.2f}")
        if h['metric']=='ctr':
            change = h['relative_change']
            if change <= -0.2:
                confidence = max(confidence,0.85)
            elif change <= -0.05:
                confidence = max(confidence,0.6)
            else:
                confidence = max(confidence,0.25)
            evidence.append(f"ctr change {change:.2f}")
        # map to label
        label = 'low'
        if confidence >= thresholds['high']:
            label = 'high'
        elif confidence >= thresholds['medium']:
            label = 'medium'
        results.append({
            'hypothesis':h['hypothesis'],
            'metric':h['metric'],
            'confidence_score':float(confidence),
            'confidence_label':label,
            'evidence':evidence
        })
    return results
