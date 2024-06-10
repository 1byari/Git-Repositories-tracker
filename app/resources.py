import json
from flask_restful import Resource
from .github_requests import get_events
from .calculations import calculate_events_statistics
from .database import parse_github_response


class EventsAPI(Resource):
    """
    This class defines an API endpoint for fetching events from multiple GitHub repositories,
    parsing the response, calculating statistics, and returning the results.
    """
    def get(self):
        """
        Handles HTTP GET requests for the /info endpoint 
        """
        with open('./config.json', 'r') as f:
            config_data = json.load(f)
        result = {"repos_time_statistics": []}
        if len(config_data['repositories']) > 5:
            raise ValueError("Number of repositories exceeds the maximum limit of 5.")
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