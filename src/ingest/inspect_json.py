# Check json structure of web
import requests, json, os
from dotenv import load_dotenv

# Load API KEY
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
if PEXELS_API_KEY is None:
    raise ValueError("API KEY not fouud")

# Standard request parameters (query, limit/pagination) used by most web APIs.
url = "https://api.pexels.com/v1/search"
params = {
    "query": "pizza",
    "per_page": 1 
}
headers = {
    "Authorization": PEXELS_API_KEY
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

# Check image structure of web
if data.get("photos"):
    img = data["photos"][0]
    print("\n=== STRUCTURE OF IMAGE ===")
    print(json.dumps(img, indent=2)) # dumps = dump to string → use to convert object (dict, list, str, int, ...) in to JSON (string)
    
    # All keys
    print("\n=== All keys ===")
    print(f"Keys: {list(img.keys())}")

print("\n=== Check Full Data Structure ===")
print(json.dumps(data, indent=2)) # dumps = dump to string → use to convert object (dict, list, str, int, ...) in to JSON (string)data