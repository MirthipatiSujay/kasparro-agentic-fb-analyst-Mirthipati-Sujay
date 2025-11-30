import argparse
import json
import time
from pathlib import Path

import yaml

from src.agents import data_agent, insight_agent, evaluator_agent, creative_agent
from src.utils.logger import log_event, log_error


def run_with_retry(agent_name, stage, func, *args, max_retries=2, backoff_seconds=1, **kwargs):
    """
    Simple retry wrapper with exponential backoff.
    Logs failures and final errors.
    """
    attempt = 0
    while True:
        start = time.monotonic()
        try:
            log_event(agent_name, stage, level="info", message="starting", attempt=attempt)
            result = func(*args, **kwargs)
            duration = time.monotonic() - start
            log_event(agent_name, stage, level="info", message="success", attempt=attempt, duration_s=duration)
            return result
        except Exception as exc:
            duration = time.monotonic() - start
            log_error(agent_name, stage, f"error on attempt {attempt}", exc)
            if attempt >= max_retries:
                # final failure
                raise
            time.sleep(backoff_seconds * (2 ** attempt))
            attempt += 1


def save_checkpoint(path: Path, state: dict):
    """
    Very lightweight checkpoint: writes JSON snapshot of intermediate state.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def main(query,
         config_path="config/config.yaml",
         data_path="data/sample_dataset.csv",
         out_dir="reports",
         logs_dir="logs"):

    cfg = yaml.safe_load(open(config_path, encoding="utf-8"))

    # 1) Data loading + summarization with retry
    summaries = run_with_retry(
        "DataAgent",
        "load_and_summarize",
        data_agent.load_and_summarize,
        data_path,
        sample=cfg.get("sample_mode", True)
    )
    save_checkpoint(Path(logs_dir) / "checkpoint_summaries.json", {"daily_rows": len(summaries["daily"])})

    # 2) Hypothesis generation
    hypotheses = run_with_retry(
        "InsightAgent",
        "generate_hypotheses",
        insight_agent.generate_hypotheses,
        summaries
    )
    save_checkpoint(Path(logs_dir) / "checkpoint_hypotheses.json", {"hypotheses": hypotheses})

    # 3) Evaluation
    evaluated = run_with_retry(
        "EvaluatorAgent",
        "evaluate_hypotheses",
        evaluator_agent.evaluate_hypotheses,
        hypotheses,
        summaries,
        cfg["confidence_thresholds"]
    )

    # 4) Creative recommendations
    creatives = run_with_retry(
        "CreativeGenerator",
        "generate_creatives",
        creative_agent.generate_creatives_for_low_ctr,
        summaries,
        low_ctr_threshold=cfg.get("low_ctr_threshold", 0.02)
    )

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    Path(logs_dir).mkdir(parents=True, exist_ok=True)

    with open(Path(out_dir) / "insights.json", "w", encoding="utf-8") as f:
        json.dump(evaluated, f, indent=2, ensure_ascii=False)

    with open(Path(out_dir) / "creatives.json", "w", encoding="utf-8") as f:
        json.dump(creatives, f, indent=2, ensure_ascii=False)

    report_md = build_report(query, evaluated, creatives)
    with open(Path(out_dir) / "report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    # High-level run log
    run_log = {
        "query": query,
        "hypothesis_count": len(hypotheses),
        "evaluated_count": len(evaluated),
        "creative_count": len(creatives),
    }
    with open(Path(logs_dir) / "run_log.json", "w", encoding="utf-8") as f:
        json.dump(run_log, f, indent=2, ensure_ascii=False)

    log_event("Orchestrator", "run_complete", level="info", message="Pipeline finished", **run_log)
    print("Outputs written to", out_dir, "and", logs_dir)


def build_report(query, evaluated, creatives):
    lines = []
    lines.append("# Agentic FB Ads Analysis Report")
    lines.append("")
    lines.append(f"**Query**: {query}")
    lines.append("")
    lines.append("## Key Insights")
    if not evaluated:
        lines.append("- No strong performance changes detected.")
    for e in evaluated:
        lines.append(
            f"- {e['hypothesis']} — confidence: {e['confidence_label']} ({e['confidence_score']:.2f})"
        )
        if e["evidence"]:
            lines.append(f"  Evidence: {', '.join(e['evidence'])}")
    lines.append("")
    lines.append("## Creative Recommendations (sample of low-CTR creatives)")
    if not creatives:
        lines.append("- No low-CTR creatives found under the configured threshold.")
    else:
        for c in creatives[:10]:
            lines.append(f"- Original: {c['original']} (ctr={c['original_ctr']:.4f})")
            for v in c["variants"]:
                lines.append(f"  - Headline: {v['headline']}")
                lines.append(f"    Body: {v['body']}")
                lines.append(f"    CTA: {v['cta']}")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, nargs="?", default="Analyze ROAS drop")
    args = parser.parse_args()
    main(args.query)
