import json
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


dbEngine = create_engine('sqlite:///events.db')
Session = sessionmaker(bind=dbEngine)
base_class = declarative_base()

class Event(base_class):
    # Class which represents Event entity in DB
    __tablename__ = 'event'
    id = Column('id', Integer, primary_key=True)
    repo = Column('repo', String)
    type = Column('type', String)
    created_at = Column('created_at', DateTime)

base_class.metadata.create_all(dbEngine)

def parse_github_response(response, repo_name):
    """
    Processes the GitHub API response and saves new events to the database.
    """
    session = Session()
    for event in response:
        save_new_data(session, event, repo_name)
    delete_extra_data(session, repo_name)
    delete_unused_repos_data(session)
    session.close()

def save_new_data(session, event, repo_name):
    """
    Saves a new event to the DB
    """
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
    """
    Deletes extra events if there are more then 500 of them for the given repository
    """
    event_count = session.query(Event).filter_by(repo=repo_name).count()
    if event_count > 500:
        oldest_events = session.query(Event).filter_by(repo=repo_name).order_by(Event.created_at).limit(event_count - 500).all()
        for event in oldest_events:
            session.delete(event)
        session.commit()

def delete_unused_repos_data(session):
    """
    Deletes events from the DB for the repositories not listed in config.json
    """
    all_repos = session.query(Event.repo).distinct().all()
    with open('./config.json', 'r') as f:
        config_data = json.load(f)
    for repo in all_repos:
        repo_name = repo[0]
        if repo_name not in config_data["repositories"]:
            session.query(Event).filter_by(repo=repo_name).delete()
        session.commit()

def convert_events_to_df(repo_name):
    """
    Converts the events for the given repository from the database to a pandas DataFrame.
    """
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
    return df