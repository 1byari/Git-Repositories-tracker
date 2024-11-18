import logging
from typing import Tuple, Dict, Any
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from api_requests.github_requests import check_repo_existance
from calculations.calculations import calculate_events_statistics
from database import functions as db_functions
from database.models import RepoModel, UserModel

endpoints = Blueprint('endpoints', __name__)

# Configure logging
logger = logging.getLogger(__name__)

def check_data_required_fields(data: Dict[str, Any], *args: str):
    """
    Checks if the required fields are present in the data.
    
    Args:
        data (Dict[str, Any]): The data to check.
        *args (str): The required field names.
    """
    missed_fields = [arg for arg in args if arg not in data]
    if missed_fields:
        return False, "Missing required fields: " + ', '.join(missed_fields)
    return True, ""

@endpoints.route('/auth/register', methods=['POST'])
def register():
    """
    Registers a new user with a hashed password and generates an access token.
    """
    data = request.get_json()
    fields_check, error_message = check_data_required_fields(data, 'username', 'password')
    if not fields_check:
        return jsonify({"message": error_message}), 400

    username = data['username']
    password = data['password']

    if UserModel.query.filter_by(username=username).first():
        return jsonify({"message": "Username is already taken"}), 400

    hashed_password = generate_password_hash(password)
    new_user = UserModel(username=username, password=hashed_password)
    new_user.save_to_db()

    access_token = create_access_token(identity=username, expires_delta=False)
    return jsonify(access_token=access_token), 200

@endpoints.route('/auth/login', methods=['POST'])
def login():
    """
    Logs in an existing user by verifying their password and generates an access token.
    """
    data = request.get_json()
    fields_check, error_message = check_data_required_fields(data, 'username', 'password')
    if not fields_check:
        return jsonify({"message": error_message}), 400

    username = data['username']
    password = data['password']

    user = UserModel.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 400

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@endpoints.route('/repository', methods=['POST'])
@jwt_required()
def add_repository():
    """
    Adds a new repository to the user's list after verifying its existence on GitHub.
    """
    username = get_jwt_identity()
    current_user = UserModel.query.filter_by(username=username).first()
    if not current_user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    fields_check, error_message = check_data_required_fields(data, 'owner', 'name')
    if not fields_check:
        return jsonify({"message": error_message}), 400

    repo_name = f"{data['owner']}/{data['name']}"
    repo = RepoModel.query.filter_by(name=repo_name).first()

    if repo is None:
        if check_repo_existance(repo_name=repo_name):
            repo = RepoModel(name=repo_name)
            repo.save_to_db()
        else:
            return jsonify({"message": "We cannot get access to this repository"}), 400

    result, message = db_functions.add_user_repo_link(user_id=current_user.id, repo_id=repo.id)
    status_code = 200 if result else 400
    return jsonify({"message": message}), status_code

@endpoints.route('/repository', methods=['DELETE'])
@jwt_required()
def delete_repository():
    """
    Deletes a repository from the user's list.
    """
    username = get_jwt_identity()
    current_user = UserModel.query.filter_by(username=username).first()
    if not current_user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    fields_check, error_message = check_data_required_fields(data, 'owner', 'name')
    if not fields_check:
        return jsonify({"message": error_message}), 400

    repo_name = f"{data['owner']}/{data['name']}"
    repo = RepoModel.query.filter_by(name=repo_name).first()

    if repo is None:
        return jsonify({"message": f"Repository {repo_name} doesn't exist"}), 400

    result, message = db_functions.delete_user_repo_link(user_id=current_user.id, repo_id=repo.id)
    status_code = 200 if result else 400
    return jsonify({"message": message}), status_code

@endpoints.route('/repository/stats', methods=['GET'])
@jwt_required()
def get_repository_stats():
    """
    Retrieves statistics for a repository in the user's list.
    """
    username = get_jwt_identity()
    current_user = UserModel.query.filter_by(username=username).first()
    if not current_user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    fields_check, error_message = check_data_required_fields(data, 'owner', 'name')
    if not fields_check:
        return jsonify({"message": error_message}), 400

    repo_name = f"{data['owner']}/{data['name']}"
    repo = RepoModel.query.filter_by(name=repo_name).first()

    if repo is None or not db_functions.check_user_repo_link(current_user.id, repo.id):
        return jsonify({"message": "You don't have this repository in your list"}), 400

    if repo.last_synced is None:
        return jsonify({"message": "We don't have any data for this repository yet"}), 400

    result = {"repositories" : []}
    statistics = calculate_events_statistics(repo.name)
    result["repositories"].append(
        {
            "repository": repo_name,
            "statistics": statistics if statistics != {} else None,
            "last_synchronized": str(repo.last_synced),
        }
    )
    return jsonify(result), 200

@endpoints.route('/repository/all/stats', methods=['GET'])
@jwt_required()
def get_all_repositories_stats():
    """
    Retrieves statistics for all of the repositories in the user's list.
    """
    username = get_jwt_identity()
    current_user = UserModel.query.filter_by(username=username).first()
    if not current_user:
        return jsonify({"message": "User not found"}), 404

    if current_user.repos is None:
        return jsonify({"message": "You don't have any repositories in your list"}), 400

    result = {"repositories" : []}
    for repo in current_user.repos:
        if repo.last_synced is None:
            result["repositories"].append(
                {
                    "repository": repo.name,
                    "statistics": None,
                    "last_synchronized": None,
                }
            )
        else:
            statistics = calculate_events_statistics(repo.name)
            result["repositories"].append(
                {
                    "repository": repo.name,
                    "statistics": statistics if statistics != {} else None,
                    "last_synchronized": str(repo.last_synced),
                }
            )

    return jsonify(result), 200
