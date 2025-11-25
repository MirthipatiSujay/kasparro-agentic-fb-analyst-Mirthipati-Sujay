Planner prompt:
- Decompose the user query into: load_data, summarize_trends, generate_hypotheses, validate, propose_creatives.
- Specify outputs in JSON for insights and creatives.

Insight prompt:
- Use the provided summaries (CTR trend, ROAS trend, spend trend).
- Produce hypotheses explaining changes, and what evidence to check.

Creative generator prompt:
- For low-CTR campaigns, look at existing creative_message and produce 3 alternative messages (headline, body, CTA).
