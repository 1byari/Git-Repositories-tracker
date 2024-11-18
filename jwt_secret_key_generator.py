import secrets
import os

jwt_secret_key = secrets.token_urlsafe(32)

print(jwt_secret_key)
os.environ["JWT_SECRET_KEY"] = jwt_secret_key

