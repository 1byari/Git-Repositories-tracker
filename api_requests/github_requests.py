import json
import logging
import time

import requests

logger = logging.getLogger(__name__)

def get_events(repo: str) -> tuple:
    """
    Fetches events for a given GitHub repository using the GitHub API.

    This function retrieves the latest events for a specified GitHub repository. 
    If the API rate limit is exceeded (HTTP status 429), it retries the request 
    with an exponential backoff mechanism.

    Args:
        repo (str): The full name of the repository in the format 'owner/repo'.

    Returns:
        tuple: A tuple containing:
            - A JSON response (dict) with the events or an error message.
            - An HTTP status code (int).
    """
    url = f'https://api.github.com/repos/{repo}/events'
    with open('./config.json', 'r') as f:
        github_token = (json.load(f))["github_access_token"]
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    max_retries = 5
    delay = 1
    
    for _ in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json(), 200
        elif response.status_code == 429:
            logger.info(f"Too many requests for '{repo}', retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
        else:
            return response.json(), response.status_code

    return {"error": "Failed to fetch events after retries"}, 429

def check_repo_existance(repo_name: str) -> bool:
    """
    Checks if a public GitHub repository exists using the GitHub API.

    This function validates the existence of a repository by sending a request
    to the GitHub API. It returns `True` if the repository exists and `False` 
    if it does not. Raises an exception for unexpected errors.

    Args:
        repo_name (str): The full name of the repository in the format 'owner/repo'.

    Returns:
        bool: 
            - `True` if the repository exists.
            - `False` if the repository does not exist (HTTP status 404).

    Raises:
        HTTPError: If the API response is an unexpected error other than 404.
    """
    url = f"https://api.github.com/repos/{repo_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        response.raise_for_status()
