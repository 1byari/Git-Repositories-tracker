# Git-Repositories-tracker

## Introduction
This program provides an API for tracking the average time between events in GitHub repositories listed in the `config.json` file.

## Requirements
- Python3 
- Python libraries from the `requirements.txt`

## Installation
1. Clone this repository to your local machine.
2. Install the required Python packages using 
```pip install -r requirements.txt```
3. Configure the `config.json` file with your GitHub access token 
4. Configure the `config.json` file with repository names in `"user/repo_name"` format (up to 5).

## Usage
1. Run the `run.py` file in the root diretory using the following command:
```python run.py```
2. Navigate to the address displayed in the terminal
3. Go to the `/info` endpoint

## Rate Limiting
This program implements rate limiting to restrict the number of requests from one user. By default, it allows:
- 200 requests per day
- 15 requests per hour
You can adjust these limits in the `app.py` file.

<img width="843" alt="image" src="https://github.com/user-attachments/assets/b46736ab-8669-460a-92a3-d0314e41ef89">

<img width="857" alt="image" src="https://github.com/user-attachments/assets/95d2bfac-a039-4b34-9efa-600e662c8fd0">

<img width="924" alt="image" src="https://github.com/user-attachments/assets/d0af3bf1-33ea-4cc1-ab3b-ad212966917c">

<img width="860" alt="image" src="https://github.com/user-attachments/assets/52dc46df-d453-48ff-89c0-333dc01127ee">

<img width="866" alt="image" src="https://github.com/user-attachments/assets/f1e25caf-60a4-4762-9e34-7a9b34920dc2">

<img width="945" alt="image" src="https://github.com/user-attachments/assets/a8f01b14-228f-4c68-b0a6-4f65c82ac770">










