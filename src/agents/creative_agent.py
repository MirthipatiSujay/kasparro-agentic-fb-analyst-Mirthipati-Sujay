import random
def generate_creatives_for_low_ctr(summaries, low_ctr_threshold=0.02, n=3):
    creative = summaries['creative']
    low = creative[creative['ctr'] < low_ctr_threshold].sort_values('ctr')
    outputs = []
    for _, row in low.head(10).iterrows():
        base = str(row['creative_message'])
        # simple variants: add urgency, social proof, benefit-first
        variants = []
        variants.append({'headline': base + ' — Limited stock!','body': base + ' Grab it before it is gone.','cta':'Shop Now'})
        variants.append({'headline': 'Loved by thousands — ' + base,'body':'Top-rated comfort and fit. See why customers choose us.','cta':'Learn More'})
        variants.append({'headline': 'New launch: ' + base,'body':'Experience our improved fabric and fit.','cta':'Buy Now'})
        outputs.append({
            'original': base,
            'original_ctr': float(row['ctr']),
            'variants': variants[:n]
        })
    return outputs
