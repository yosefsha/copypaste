import os


class Config:
    DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL") or None
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    PASTE_TABLE_NAME = os.environ.get("PASTE_TABLE_NAME", "pastes")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
