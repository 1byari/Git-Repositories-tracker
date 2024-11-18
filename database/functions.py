import logging
from datetime import UTC, datetime, timedelta
import pandas as pd

from api_requests.github_requests import get_events
from database.models import EventModel, RepoModel, UserModel, UserRepoModel
from . import db


logger = logging.getLogger(__name__)

def check_if_user_exists(username: str) -> bool:
    """
    Checks if a user exists in the database by username.
    
    Args:
        username (str): The username to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return UserModel.query.filter_by(username=username).first() is not None

def check_user_repo_link(user_id: int, repo_id: int) -> bool:
    """
    Checks if a repository is linked to a user.

    Args:
        user_id (int): The ID of the user.
        repo_id (int): The ID of the repository.

    Returns:
        bool: True if the link exists, False otherwise.
    """
    existing_link = UserRepoModel.query.filter_by(user_id=user_id, repo_id=repo_id).first()
    return existing_link is not None

def add_user_repo_link(user_id: int, repo_id: int) -> tuple:
    """
    Adds a link between a user and a repository if the user has fewer than 5 repositories.

    Args:
        user_id (int): The ID of the user.
        repo_id (int): The ID of the repository.

    Returns:
        tuple: A tuple (bool, str) indicating success or failure and a message.
    """
    if check_user_repo_link(user_id, repo_id):
        return False, 'Repository is already added'
    elif len(UserRepoModel.query.filter_by(user_id=user_id).all()) >= 5:
        return False, 'You cannot add more than 5 repositories'
    else:
        new_link = UserRepoModel(user_id=user_id, repo_id=repo_id)
        db.session.add(new_link)
        db.session.commit()
        return True, 'Repository was added'

def delete_user_repo_link(user_id: int, repo_id: int) -> tuple:
    """
    Deletes the link between a user and a repository.

    Args:
        user_id (int): The ID of the user.
        repo_id (int): The ID of the repository.

    Returns:
        tuple: A tuple (bool, str) indicating success or failure and a message.
    """
    rows = UserRepoModel.query.filter_by(user_id=user_id, repo_id=repo_id).delete()
    db.session.commit()
    if rows > 0:
        return True, 'Repository was removed'
    else:
        return False, 'You do not have this repository'

def save_new_event(event: dict, repo: RepoModel) -> None:
    """
    Saves a new event to the database if it does not already exist.

    Args:
        event (dict): The event data as a dictionary.
        repo (RepoModel): The repository associated with the event.
    """
    event_existence = EventModel.query.filter_by(id=event['id']).first()
    if not event_existence:
        new_event = EventModel(
            id=event['id'],
            type=event['type'],
            created_at=datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
            repository=repo
        )
        db.session.add(new_event)
        db.session.commit()

def delete_extra_events(repo_id: int) -> None:
    """
    Deletes events if there are more than 500 for the given repository to save storage space.

    Args:
        repo_id (int): The ID of the repository.
    """
    event_count = EventModel.query.filter_by(repository_id=repo_id).count()
    if event_count > 500:
        oldest_events = EventModel.query.filter_by(repository_id=repo_id).order_by(EventModel.created_at).limit(event_count - 500).all()
        for event in oldest_events:
            db.session.delete(event)
        db.session.commit()

# def delete_unused_repos_data():
#     """
#     Deletes events from the database for repositories not listed in config.json.
#     This function is currently commented out.
#     """
#     all_repos = db.session.query(EventModel.repo).distinct().all()
#     with open('./config.json', 'r') as f:
#         config_data = json.load(f)
#     for repo in all_repos:
#         repo_name = repo[0]
#         if repo_name not in config_data["repositories"]:
#             db.session.query(EventModel).filter_by(repo=repo_name).delete()
#         db.session.commit()

def synchronize_db_events() -> None:
    """
    Synchronizes events for repositories that have not been updated in the last 5 minutes.
    Retrieves new events from GitHub and saves them to the database.
    """
    logger.info('Synchronization started')

    five_minutes_ago = datetime.now(UTC) - timedelta(minutes=5)
    repos_to_sync = RepoModel.query.filter(
        (RepoModel.last_synced == None) | (RepoModel.last_synced < five_minutes_ago)
    ).all()

    if not repos_to_sync:
        logger.debug('No repositories to update')
        return

    for repo in repos_to_sync:
        response, status_code = get_events(repo.name)

        if status_code == 200:
            logger.debug(f'{repo.name} events were received')
            for event in response:
                save_new_event(event, repo)
            delete_extra_events(repo.id)
            repo.last_synced = datetime.now(UTC)
        else:
            logger.error(f'Error while receiving new events for {repo.name}: {response}')

    db.session.commit()
    db.session.close()
    logger.info('Synchronization was completed successfully')

def convert_events_to_df(repo_name: str) -> pd.DataFrame:
    """
    Converts the events for the given repository from the database to a pandas DataFrame.

    Args:
        repo_name (str): The name of the repository.

    Returns:
        pd.DataFrame: A DataFrame containing the events data for the repository.
    """
    query = f"""
    SELECT event.id, repository.name, event.type, event.created_at
    FROM event JOIN repository
    ON event.repository_id = repository.id
    WHERE repository.name = '{repo_name}'
    ORDER BY created_at DESC
    """
    df = pd.read_sql_query(
        sql=query,
        con=db.engine
    )
    db.session.close()
    return df
