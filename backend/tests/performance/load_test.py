from locust import User, task, between
import sys
import os

# Dynamically add project root (samsubot/) to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now this import will work

from backend.apps.rag.query import ask_question

class RAGUser(User):
    wait_time = between(1, 2)

    @task
    def ask_question_task(self):
        # Call your function directly
        response = ask_question("What is SamsuBot?")
        # Optionally print results (but too many prints slow down test)
        # print(response)