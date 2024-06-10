import requests
import json

def get_events(repo):
    """
    Fetches events for a given GitHub repository.
    """
    url = f'https://api.github.com/repos/{repo}/events'
    with open('./config.json', 'r') as f:
        github_token = (json.load(f))["github_access_token"]
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json(), 200
    return response.json(), response.status_code