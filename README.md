# Git-Repositories-tracker

## Introduction
This API allows users to manage and track GitHub repositories for events. It supports user authentication, repository management, and provides statistics for tracked repositories.

## Requirements
- Python3 
- Python libraries from the `requirements.txt`

## Installation
1. Clone this repository to your local machine.
2. Install the required Python packages using 
```pip install -r requirements.txt```
3. Configure the `config.json` file with your GitHub access token
4. Run the `jwt_secret_key_generator.py` file to configure JWT secret key for your project

## Usage
1. Run the `run.py` file in the root diretory using the following command:
```python run.py```
2. Navigate to the address displayed in the terminal

---

## API Endpoints

### Authentication Endpoints

#### 1. Register - `/auth/register`
- **Method**: `POST`
- **Description**: Register a new user in the system.
- **Request Body**:
  ```json
  {
      "username": "string",
      "password": "string"
  }
  ```
- **Response**:
  - **200 OK**: Returns a JSON object containing a JWT token for the registered user.
    ```json
    {
        "access_token": "your_jwt_token_here"
    }
    ```
  - **400 Bad Request**: If the username is already taken or required fields are missing.
    <img width="843" alt="image" src="https://github.com/user-attachments/assets/b46736ab-8669-460a-92a3-d0314e41ef89">

#### 2. Login - `/auth/login`
- **Method**: `POST`
- **Description**: Log in an existing user and generate a JWT token.
- **Request Body**:
  ```json
  {
      "username": "string",
      "password": "string"
  }
  ```
- **Response**:
  - **200 OK**: Returns a JSON object containing a JWT token for the user.
    ```json
    {
        "access_token": "your_jwt_token_here"
    }
    ```
  - **400 Bad Request**: If the username or password is incorrect.
    <img width="857" alt="image" src="https://github.com/user-attachments/assets/95d2bfac-a039-4b34-9efa-600e662c8fd0">

---

### Repository Endpoints

#### 3. Add Repository - `/repositories`
- **Method**: `POST`
- **Description**: Add a GitHub repository to the authenticated user's list.
- **Request Body**:
  ```json
  {
      "owner": "string",
      "name": "string"
  }
  ```
- **Response**:
  - **200 OK**: Repository successfully added.
    ```json
    {
        "message": "Repository was added"
    }
    ```
  - **400 Bad Request**: If the repository already exists or cannot be accessed.
    <img width="924" alt="image" src="https://github.com/user-attachments/assets/d0af3bf1-33ea-4cc1-ab3b-ad212966917c">

#### 4. Delete Repository - `/repositories`
- **Method**: `DELETE`
- **Description**: Remove a GitHub repository from the authenticated user's list.
- **Request Body**:
  ```json
  {
      "owner": "string",
      "name": "string"
  }
  ```
- **Response**:
  - **200 OK**: Repository successfully removed.
    ```json
    {
        "message": "Repository was removed"
    }
    ```
  - **400 Bad Request**: If the repository does not exist in the user's list.
    <img width="860" alt="image" src="https://github.com/user-attachments/assets/52dc46df-d453-48ff-89c0-333dc01127ee">

#### 5. Get Repository Statistics - `/repository/stats`, `/repository/all/stats`
- **Method**: `GET`
- **Description**: Retrieve statistics for a specified repository or all repositories in the user's list.
- **Request Body** (optional):
  ```json
  {
      "owner": "string",
      "name": "string"
  }
  ```
- **Response**:
  - **200 OK**: 
    - For a specific repository:
      ```json
      {
          "repository": "owner/repo-name",
          "statistics": { /* statistics data */ },
          "last_synchronized": "2023-12-01T10:00:00"
      }
      ```
    - For all repositories:
      ```json
      {
          "repositories_statistics": [
              {
                  "repository": "owner1/repo1",
                  "statistics": { /* statistics data */ },
                  "last_synchronized": "2023-12-01T10:00:00"
              },
              {
                  "repository": "owner2/repo2",
                  "statistics": { /* statistics data */ },
                  "last_synchronized": "2023-12-02T11:30:00"
              }
          ]
      }
      ```
  - **400 Bad Request**: If the repository does not exist or has no data.
    <img width="866" alt="image" src="https://github.com/user-attachments/assets/f1e25caf-60a4-4762-9e34-7a9b34920dc2">
 
---

## How Event Synchronization Works

The system periodically synchronizes events from GitHub repositories using the following process:

1. **Triggering Synchronization**:
   - A background job runs every 5 minutes to check for repositories that need synchronization.
   - Repositories are synchronized if:
     - They have never been synced before.
     - The last synchronization occurred more than 5 minutes ago.

2. **Fetching Events**:
   - The system sends a request to the GitHub API to fetch the latest events for each repository.

3. **Saving Events**:
   - Each event is checked against the database to ensure no duplicates are saved.
   - New events are added to the database, linked to their respective repositories.

4. **Trimming Events**:
   - If a repository exceeds 500 events in the database, the oldest events are deleted to maintain efficiency.

5. **Error Handling**:
   - If GitHub API rate limits are exceeded, the system retries after a delay.
   - Failed repositories are logged for review.

6. **Updating Synchronization Timestamp**:
   - After successful synchronization, the `last_synced` timestamp for each repository is updated.
  
     <img width="945" alt="image" src="https://github.com/user-attachments/assets/a8f01b14-228f-4c68-b0a6-4f65c82ac770">

---

## Rate Limiting
The API implements rate limiting to manage requests:
- **200 requests per day**
- **15 requests per hour**
These limits can be configured in the application.

---

## Example Errors

- **Missing Fields**:
  ```json
  {
      "message": "Missing required fields: owner, name"
  }
  ```

- **Repository Not Found**:
  ```json
  {
      "message": "Repository does not exist"
  }
  ```

---

## How to Use
1. Authenticate using the `/auth/register` or `/auth/login` endpoints to get a JWT token.
2. Use the token to interact with repository endpoints (`/repositories` and `/repository/stats`) by including it in the `Authorization` header:
   ```
   Authorization: Bearer <your_jwt_token>
   ```

---
























