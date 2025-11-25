# Agent Graph & Roles

Planner -> DataAgent -> InsightAgent -> EvaluatorAgent -> CreativeGenerator

- Planner Agent: Receives user query, defines subtasks and orchestrates agents.
- Data Agent: Loads, cleans, and summarizes dataset. Produces aggregated summaries (by date, campaign, creative_type).
- Insight Agent: Generates hypotheses from summaries (e.g., CTR drop, spend shift, audience change).
- Evaluator Agent: Tests hypotheses with quantitative checks, computes confidence scores and evidence.
- Creative Improvement Generator: For low-CTR campaigns, generates new creative messages grounded in existing creative_message examples.
