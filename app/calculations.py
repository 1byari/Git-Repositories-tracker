import pandas as pd
from datetime import datetime, timedelta, UTC
from .database import convert_events_to_df


def calculate_events_statistics(repo_name):
    df = convert_events_to_df(repo_name)
    week_ago_date = (datetime.now(UTC) - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    last_week_events = df[df.created_at > week_ago_date]
    if len(last_week_events) <= 500 and len(last_week_events) > 0:
        data = last_week_events
    else:
        data = df.head(500)
    data['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    data['time_delta'] = data.groupby('type')['created_at'].diff(1).dt.total_seconds().abs()
    average_data = data.groupby('type')['time_delta'].mean().fillna(0).round(3)
    return average_data.to_dict()