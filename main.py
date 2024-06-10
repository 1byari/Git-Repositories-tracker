from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask
from flask_restful import Api, Resource
import requests
import json
import pandas as pd
from datetime import datetime, timedelta, UTC

app = Flask(__name__)
api = Api(app)

def get_events(repo):
    url = f'https://api.github.com/repos/{repo}/events'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), 200
    return response.json(), response.status_code

dbEngine = create_engine('sqlite:///events.db')
Session = sessionmaker(bind=dbEngine)
base_class = declarative_base()
    


class Event(base_class):
    __tablename__ = 'event'
    id = Column('id', Integer, primary_key=True)
    repo = Column('repo', String)
    type = Column('type', String)
    created_at = Column('created_at', DateTime)
    
base_class.metadata.create_all(dbEngine)

def parse_github_response(response, repo_name):
    session = Session()
    for event in response:
        save_new_data(session, event, repo_name)
    delete_extra_data(session, repo_name)
    session.close()

def save_new_data(session, event, repo_name):
    event_existence = session.query(Event).filter_by(id=event['id']).first()
    if not event_existence:
        event_db = Event(
            id=event['id'],
            repo=repo_name,
            type=event['type'],
            created_at=datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        )
        session.add(event_db)
        session.commit()

def delete_extra_data(session, repo_name):
    event_count = session.query(Event).filter_by(repo=repo_name).count()
    if event_count > 500:
        oldest_events = session.query(Event).filter_by(repo=repo_name).order_by(Event.created_at).limit(event_count - 500).all()
        for event in oldest_events:
            session.delete(event)
        session.commit()

def calculate_events_statistics(repo_name):
    session = Session()
    query = f"""
    SELECT id, repo, type, created_at
    FROM event
    WHERE repo = '{repo_name}'
    ORDER BY created_at DESC
    """
    df = pd.read_sql_query(
        sql = query,
        con = dbEngine
    )
    session.close()
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
    


class EventsAPI(Resource):
    def get(self):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        result = {"repos_time_statistics": []}
        for repo_name in config_data['repositories']:
            response, code = get_events(repo_name)
            if code != 200:
                return response, code
            parse_github_response(response, repo_name)
            statistics = calculate_events_statistics(repo_name)
            result['repos_time_statistics'].append(
                {
                    "repository": repo_name,
                    "statistics": statistics
                }
            )
        return result, 200
            

api.add_resource(EventsAPI, "/info")

if __name__ == '__main__':
    app.run(debug=True)
    

    