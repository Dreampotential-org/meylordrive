import requests

headers = {}


body={
    'input_content': 'how to install python on windows'
}
req = requests.post(
    #"http://localhost:8000/ai/input-chat/", headers=headers, json=body)
    "https://api.dreampotential.org/ai/input-chat/", headers=headers, json=body)

print(req.text)
import os
os.exit()



body={
    'upload_id': 4,
    'message': 'okay this is great'
}
req = requests.post(
    "http://localhost:8000/storage/add_comment/", headers=headers, json=body)

print(req.json())


req = requests.get(
    "http://localhost:8000/storage/list_comments/4", headers=headers, json=body)

print(req.json())
