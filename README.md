# Git-Repositories-tracker

## Introduction
This program provides an API for tracking the average time between events in GitHub repositories listed in the `config.json` file.

## Requirements
- Python3 
- Python libraries from the requirements.txt

## Installation
1. Clone this repository to your local machine.
2. Install the required Python packages using pip install < requirements.txt:
3. Configure the `config.json` file with your GitHub access token 
4. Configure the `config.json` file with repository names in "user/repo_name" format (up to 5).

## Usage
1. Run the `app.py` file:
2. Navigate to the address displayed address
3. Go to the /info endpoint

## Rate Limiting
This program implements rate limiting to restrict the number of requests from one user. By default, it allows:
- 200 requests per day
- 15 requests per hour
You can adjust these limits in the `app.py` file.







