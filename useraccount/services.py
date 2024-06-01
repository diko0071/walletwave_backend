import requests 
import os
from .models import User


def email_welcome(user_id):

    user = User.objects.get(id=user_id)
    email, name = user.email, user.name

    url = "https://app.loops.so/api/v1/transactional"

    if name is None:
        name = ""

    payload = {
        "transactionalId": "clwvcdnog01pwirs9u46uqdf2",
        "email": email,
        "dataVariables": {
            "name": name,
        }
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('LOOPS_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()