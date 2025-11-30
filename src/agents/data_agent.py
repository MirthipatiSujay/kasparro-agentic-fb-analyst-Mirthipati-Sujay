import pandas as pd
from pathlib import Path

from src.utils.logger import log_event, log_error


REQUIRED_COLUMNS = [
    "campaign_name",
    "adset_name",
    "date",
    "spend",
    "impressions",
    "clicks",
    "purchases",
    "revenue",
    "creative_type",
    "creative_message",
    "audience_type",
    "platform",
    "country",
]

NUMERIC_COLUMNS = ["spend", "impressions", "clicks", "purchases", "revenue"]


def _validate_schema(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Try to coerce numeric columns
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Warn if many nulls after coercion
    null_info = {
        col: int(df[col].isna().sum())
        for col in NUMERIC_COLUMNS
    }
    log_event("DataAgent", "schema_validation", level="info",
              message="schema validated", null_counts=null_info)


def load_and_summarize(path, sample=True, nrows=None):
    path = Path(path)
    log_event("DataAgent", "load_data", message="loading CSV", filename=str(path))
    df = pd.read_csv(path)

    _validate_schema(df)

    df["date"] = pd.to_datetime(df["date"])

    if sample and nrows is None:
        df = df.sample(frac=0.25, random_state=42)
    if nrows:
        df = df.head(nrows)

    daily = df.groupby("date").agg({
        "spend": "sum",
        "impressions": "sum",
        "clicks": "sum",
        "purchases": "sum",
        "revenue": "sum"
    }).reset_index()
    daily["ctr"] = daily["clicks"] / daily["impressions"].replace({0: 1})
    daily["roas"] = daily["revenue"] / daily["spend"].replace({0: 1})

    campaign = df.groupby("campaign_name").agg({
        "spend": "sum",
        "impressions": "sum",
        "clicks": "sum",
        "purchases": "sum",
        "revenue": "sum"
    }).reset_index()
    campaign["ctr"] = campaign["clicks"] / campaign["impressions"].replace({0: 1})
    campaign["roas"] = campaign["revenue"] / campaign["spend"].replace({0: 1})

    creative = df.groupby("creative_message").agg({
        "spend": "sum",
        "impressions": "sum",
        "clicks": "sum",
        "purchases": "sum",
        "revenue": "sum"
    }).reset_index()
    creative["ctr"] = creative["clicks"] / creative["impressions"].replace({0: 1})
    creative["roas"] = creative["revenue"] / creative["spend"].replace({0: 1})

    log_event("DataAgent", "summaries_built", message="built summaries",
              daily_rows=len(daily),
              campaign_rows=len(campaign),
              creative_rows=len(creative))

    return {"raw": df, "daily": daily, "campaign": campaign, "creative": creative}
