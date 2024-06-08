import requests

def get_events(repo):
    url = f'https://api.github.com/repos/{repo}/events'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), 200
    return response.json(), response.status_code