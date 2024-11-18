from datetime import UTC, datetime, timedelta

import pandas as pd

from database.functions import convert_events_to_df


def calculate_events_statistics(repo_name: str) -> dict:
    """
    Calculate the average time delta between events of each type for a given repository.

    This function analyzes the events for a specific GitHub repository and calculates
    the average time difference (in seconds) between consecutive events of each type
    in the last 7 days. If the repository has fewer than 500 events in the past week,
    all events are analyzed. Otherwise, the most recent 500 events are used.

    Args:
        repo_name (str): The name of the repository in the format 'owner/repo'.

    Returns:
        dict: A dictionary where keys are event types, and values are the average time 
              difference in seconds between events of that type.
    """
    df = convert_events_to_df(repo_name)
    week_ago_date = (datetime.now(UTC) - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    last_week_events = df[df.created_at > week_ago_date]

    if len(last_week_events) <= 500 and len(last_week_events) > 0:
        data = last_week_events
    else:
        data = df.head(500)
    
    # Convert the 'created_at' column to datetime
    data['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Calculates the average time delta for each event type
    data['time_delta'] = data.groupby('type')['created_at'].diff(1).dt.total_seconds().abs()
    average_data = data.groupby('type')['time_delta'].mean().fillna(0).round(3)
    return average_data.to_dict()