import os
import requests
import yaml

# Load Config
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

api_key = config.get("api", {}).get("key")
base_url = config.get("api", {}).get("base_url", "https://api.openai.com/v1")

print(f"Checking models with API Key: {api_key[:8]}...{api_key[-4:]}")

headers = {
    "Authorization": f"Bearer {api_key}"
}

try:
    response = requests.get(f"{base_url}/models", headers=headers)
    if response.status_code == 200:
        models = response.json()['data']
        print(f"SUCCESS: Found {len(models)} models.")
        gpt4o = any(m['id'] == 'gpt-4o' for m in models)
        gpt4o_mini = any(m['id'] == 'gpt-4o-mini' for m in models)
        print(f" - gpt-4o available: {gpt4o}")
        print(f" - gpt-4o-mini available: {gpt4o_mini}")
    else:
        print(f"FAILED: Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"ERROR: {e}")
