import time

import requests

# Define the URL
url = "http://localhost:8000/api/stats"

try:
    # Send a GET request
    while True:
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response content
            print(response.json())
        else:
            print(f"Request failed with status code: {response.status_code}")

        time.sleep(5)
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")