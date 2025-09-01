import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "mistral",
    "prompt": "Write a short poem about AI."
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.text)