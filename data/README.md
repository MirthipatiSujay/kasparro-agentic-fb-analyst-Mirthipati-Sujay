# Dataset Documentation

This folder contains the **sample dataset** used by the Agentic Facebook Performance Analyst system.  
It is a small synthetic subset of a larger performance marketing dataset and is included only to allow evaluators to run the system quickly and verify outputs.

---

## 📁 Files Included

### `sample_dataset.csv`
A compact dataset containing daily Facebook Ad performance metrics, campaign metadata, and creative attributes.

This dataset is intentionally small to:
- Support fast execution
- Enable reproducible insights
- Demonstrate hypothesis generation, evaluation, and creative recommendations

---

## 🧾 Column Descriptions

| Column | Meaning |
|-------|---------|
| `campaign_name` | Name of the Facebook Ads campaign |
| `adset_name` | Targeting layer within the campaign |
| `date` | Calendar date of the metric record |
| `spend` | Amount spent on ads for the given date |
| `impressions` | Number of times ads were shown to users |
| `clicks` | Total number of clicks received |
| `ctr` | Click-Through Rate = clicks / impressions |
| `purchases` | Count of purchases attributed to the ad |
| `revenue` | Revenue generated from purchases |
| `roas` | Return on Ad Spend = revenue / spend |
| `creative_type` | Format of the ad (e.g., static image, carousel, UGC video) |
| `creative_message` | Primary text/copy used in the creative |
| `audience_type` | Audience segment type (e.g., lookalike, retargeting, broad) |
| `platform` | Platform where the ad was served (e.g., Facebook, Instagram) |
| `country` | Geographical targeting of the ad |

---

## 🎯 Purpose of This Dataset

The sample dataset is used to:

✔ Generate hypotheses on campaign performance trends  
✔ Evaluate changes in ROAS, CTR, and spend using the Evaluator Agent  
✔ Provide data-grounded creative improvement suggestions  
✔ Validate the end-to-end functioning of the agentic workflow

This dataset is **not** intended for production use or large-scale machine learning tasks.

---

## 📝 Notes

- The data values are synthetic for demonstration purposes.
- Larger datasets should NOT be included in this repository.
- Evaluators can modify this CSV to test different insights.
