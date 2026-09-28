import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("TYPESAFE_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": os.getenv("JEV_MODEL", "typesafe/jev-1.13"),
    "messages": [
        {"role": "user", "content": "Hello"}
    ]
}

print("Testing OpenRouter models endpoint...")
res = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
print("Models status:", res.status_code)
if res.status_code == 200:
    models = [m['id'] for m in res.json().get('data', []) if 'jev' in m['id'].lower() or 'typesafe' in m['id'].lower()]
    print("Matching JEV/Typesafe models:", models)

print("\nTesting OpenRouter completions endpoint with model typesafe/jev-1.13...")
res2 = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
print("Chat completion status:", res2.status_code)
print("Response:", res2.text[:500])

