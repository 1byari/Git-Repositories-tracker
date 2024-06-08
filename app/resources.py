import json
from flask_restful import Resource
from .github_requests import get_events
from .calculations import calculate_events_statistics
from .database import parse_github_response


class EventsAPI(Resource):
    def get(self):
        with open('./config.json', 'r') as f:
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