import os
import subprocess

def run_command(user_input):
    """Execute a command from user input"""
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout.decode()

def get_user_data(user_id):
    """Fetch user data"""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # TODO: connect to database
    return query

API_KEY = "sk-1234567890abcdef"

def divide(a, b):
    return a / b
