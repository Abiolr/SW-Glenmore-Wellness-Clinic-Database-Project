from fastapi import Depends


def common_dependencies():
    # add shared dependencies (auth, db) here
    return {}


def get_current_user():
    # placeholder dependency
    return {"username": "anonymous"}
