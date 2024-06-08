import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


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

def convert_events_to_df(repo_name):
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