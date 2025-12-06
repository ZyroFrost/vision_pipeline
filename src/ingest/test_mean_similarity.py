import os, requests
from dotenv import load_dotenv
from transformers import SiglipModel

load_dotenv()
PIXELS_API_KEY = os.getenv("PEXELS_API_KEY")
if PIXELS_API_KEY is None:
    raise ValueError("API KEY not fouud")

# Standard request parameters (query, limit/pagination) used by most web APIs.
headers = {"Authorization": PIXELS_API_KEY }
url = "https://api.pexels.com/v1/search"
params = {
    "query": "pizza",
    "per_page": 80
}
def download_image(query: str, page: int, per_page: int = 80):
    headers = {"Authorization": PIXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "page": page, "per_page": per_page,}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    query = "tacos"

    try:
        resp = download_image(query, page=1)
        batch = resp.get("photos")
    except Exception as e:
        print(f"❌ Cannot download image: {e}")
        exit(1) # eixit(1) mean for response code or image not found

    if not batch:
        print(f"❌ No images found for query: {query}")
        exit(1)
        
    for img in batch:
        img_url = img.get("src", {}).get("original")


        
    print(data)