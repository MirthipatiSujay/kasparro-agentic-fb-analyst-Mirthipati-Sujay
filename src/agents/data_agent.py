import pandas as pd
from pathlib import Path
def load_and_summarize(path, sample=True, nrows=None):
    df = pd.read_csv(path)
    # basic cleaning
    df['date'] = pd.to_datetime(df['date'])
    # sample if needed
    if sample and nrows is None:
        df = df.sample(frac=0.25, random_state=42)
    if nrows:
        df = df.head(nrows)
    # global summaries
    daily = df.groupby('date').agg({
        'spend':'sum',
        'impressions':'sum',
        'clicks':'sum',
        'purchases':'sum',
        'revenue':'sum'
    }).reset_index()
    daily['ctr'] = daily['clicks'] / daily['impressions']
    daily['roas'] = daily['revenue'] / (daily['spend'].replace({0:1}))
    # campaign summaries
    campaign = df.groupby('campaign_name').agg({
        'spend':'sum','impressions':'sum','clicks':'sum','purchases':'sum','revenue':'sum'
    }).reset_index()
    campaign['ctr'] = campaign['clicks'] / campaign['impressions']
    campaign['roas'] = campaign['revenue'] / (campaign['spend'].replace({0:1}))
    # creative level
    creative = df.groupby('creative_message').agg({
        'spend':'sum','impressions':'sum','clicks':'sum','purchases':'sum','revenue':'sum'
    }).reset_index()
    creative['ctr'] = creative['clicks'] / creative['impressions']
    creative['roas'] = creative['revenue'] / (creative['spend'].replace({0:1}))
    return {'raw':df, 'daily':daily, 'campaign':campaign, 'creative':creative}
