def generate_hypotheses(summaries):
    daily = summaries['daily']
    # compute recent ROAS change (last vs previous week mean)
    daily_sorted = daily.sort_values('date')
    if len(daily_sorted) < 14:
        # fallback
        recent = daily_sorted.tail(7)
        prev = daily_sorted.head(max(0, len(daily_sorted)-7))
    else:
        recent = daily_sorted.tail(7)
        prev = daily_sorted.tail(14).head(7)
    recent_roas = recent['roas'].mean()
    prev_roas = prev['roas'].mean() if len(prev)>0 else recent_roas
    roas_change = (recent_roas - prev_roas) / (prev_roas if prev_roas!=0 else 1)
    # check CTR change
    recent_ctr = recent['ctr'].mean()
    prev_ctr = prev['ctr'].mean() if len(prev)>0 else recent_ctr
    ctr_change = (recent_ctr - prev_ctr) / (prev_ctr if prev_ctr!=0 else 1)
    hypotheses = []
    if roas_change < -0.05:
        hypotheses.append({
            'hypothesis': 'ROAS dropped recently',
            'metric':'roas',
            'recent_mean':float(recent_roas),
            'previous_mean':float(prev_roas),
            'relative_change':float(roas_change)
        })
        # if CTR dropped significantly
        if ctr_change < -0.05:
            hypotheses.append({
                'hypothesis':'CTR dropped and may explain ROAS drop',
                'metric':'ctr',
                'recent_mean':float(recent_ctr),
                'previous_mean':float(prev_ctr),
                'relative_change':float(ctr_change)
            })
    else:
        hypotheses.append({
            'hypothesis':'No major ROAS drop detected',
            'metric':'roas',
            'recent_mean':float(recent_roas),
            'previous_mean':float(prev_roas),
            'relative_change':float(roas_change)
        })
    return hypotheses
