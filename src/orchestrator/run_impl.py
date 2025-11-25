import argparse, json, yaml
from pathlib import Path
from src.agents import data_agent, insight_agent, evaluator_agent, creative_agent
def main(query, config_path='config/config.yaml', data_path='data/sample_dataset.csv', out_dir='reports', logs_dir='logs'):
    # load config
    import yaml
    cfg = yaml.safe_load(open(config_path))
    summaries = data_agent.load_and_summarize(data_path, sample=cfg.get('sample_mode', True))
    hypotheses = insight_agent.generate_hypotheses(summaries)
    evaluated = evaluator_agent.evaluate_hypotheses(hypotheses, summaries, cfg['confidence_thresholds'])
    creatives = creative_agent.generate_creatives_for_low_ctr(summaries, low_ctr_threshold=cfg.get('low_ctr_threshold',0.02))
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    # save outputs
    with open(Path(out_dir)/'insights.json','w', encoding='utf-8') as f:
        json.dump(evaluated, f, indent=2, ensure_ascii=False)

    with open(Path(out_dir)/'creatives.json','w', encoding='utf-8') as f:
        json.dump(creatives, f, indent=2, ensure_ascii=False)

    report_md = build_report(query, evaluated, creatives)
    with open(Path(out_dir)/'report.md','w', encoding='utf-8') as f:
        f.write(report_md)

    # logs
    log = {'query':query,'timestamp':str(__import__('datetime').datetime.utcnow()), 'hypotheses':hypotheses}
    with open(Path(logs_dir)/'run_log.json','w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    print('Outputs written to', out_dir, 'and', logs_dir)

def build_report(query, evaluated, creatives):
    lines = []
    lines.append('# Agentic FB Ads Analysis Report')
    lines.append('')
    lines.append(f'**Query**: {query}')
    lines.append('')
    lines.append('## Key Insights')
    for e in evaluated:
        lines.append(f"- {e['hypothesis']} — confidence: {e['confidence_label']} ({e['confidence_score']:.2f})")
        lines.append(f"  Evidence: {', '.join(e['evidence'])}")
    lines.append('')
    lines.append('## Creative Recommendations (for sample low-CTR creatives)')
    if not creatives:
        lines.append('- No low-CTR creatives found under the configured threshold.')
    for c in creatives[:10]:
        lines.append(f"- Original: {c['original']} (ctr={c['original_ctr']:.4f})")
        for v in c['variants']:
            lines.append(f"  - Headline: {v['headline']}")
            lines.append(f"    Body: {v['body']}")
            lines.append(f"    CTA: {v['cta']}")
    return '\n'.join(lines)

if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('query', type=str)
    args = p.parse_args()
    main(args.query)
