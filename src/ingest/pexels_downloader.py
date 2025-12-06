import os, requests, time, math
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from clip_filter import is_image_relevant
from datetime import datetime

# Load API key
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
if PEXELS_API_KEY is None:
    raise ValueError("❌ API key not found. Please check the .env file.")

# Configure directories
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" 
META_DIR = ROOT / "data" / "metadata"
RAW_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

# Set up API headers with authentication for Pexels API requests.
# per_page = 80 (maximum allowed by Pexels)
def download_image(query: str, page: int, per_page: int = 80):
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "page": page, "per_page": per_page,}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    # Main var 
    query_folder = "tacos"
    query = "tacos"
    target_count = 1000 
    similarity = 0.25
    saved_img = 0

    meta_path = META_DIR / f"{query_folder}_metadata.csv"
    query_dir = RAW_DIR / query_folder
    query_dir.mkdir(parents=True, exist_ok=True)

    already_has = len(os.listdir(query_dir))
    already_has_not_change = len(os.listdir(query_dir))
    downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0

    print(f"Images already in folder {query}: {already_has}")
    print(f"Metadata entries already in file: {downloaded_meta}")
    print(f"Download progress for {query}: {already_has}/{target_count}")

    # First call to get total_results
    first_resp = download_image(query, page=1) 
    total_results = first_resp.get("total_results", 0)
    max_page = math.ceil(total_results / 80)

    print(f"Total results from API: {total_results}")
    print(f"Target will scan up to {max_page} pages.")
    print(f"Maximum images per page: 80")

    for page in range(1, max_page + 1):

        already_has = len(os.listdir(query_dir))
        if already_has >= target_count:
            print("🎉 Reached target count!")
            break

        print(f"\n📄 Fetching page {page} ...")
        try:
            resp = download_image(query, page=page)  # resp is the full API response
            batch = resp.get("photos", []) # metadata to check image
            print("✅ Metadata batch fetched successfully.")
        except Exception as e:
            print(f"❌ Failed to fetch metadata batch: {e}")
            time.sleep(2)
            continue

        if not batch:
            print("⚠️ No more images returned by API.")
            break
        
        for idi, img in enumerate(batch):
            already_has = len(os.listdir(query_dir))
            downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0

            if already_has >= target_count:
                print("🎉 Reached target count!")
                break
            img_url = img.get("src", {}).get("original")
            img_id = img.get("id")  # or any other unique identifier for the image
            img_ext = "jpg"
            img_filename = f"{query_folder}_{img_id}.{img_ext}"
            img_path = query_dir / img_filename

            if img_path.exists():
                print(f"❌ [{idi}] Image {img_id} already exists in folder. Skipped.")
                continue

            # CLIP filter
            ok, score = is_image_relevant(img_url, query, similarity)
            if not ok:
                print(f"❌ [{idi}] Image {img_id} (similarity = {score:.2f}) does not match the query '{query}'. Skipped.")
                continue
            
            # Save images & metadata
            try: 
                img_resp = requests.get(img_url, timeout=10)
                img_resp.raise_for_status() # 
                with open(img_path, "wb") as f:
                    f.write(img_resp.content)
                
                metadata_row = {
                    "id": img_id,
                    "query": query,
                    "filename": img_filename,
                    "url": img_url,
                    "downloaded_at": datetime.now().isoformat()
                }
                df = pd.DataFrame([metadata_row]) # Use list to make row

                if meta_path.exists():
                    df.to_csv(meta_path, mode='a', header=False, index=False) #  a = append, write data at last row                  
                else:
                    df.to_csv(meta_path, index=False) # Save new if file no not exists

                saved_img += 1   
                downloaded_meta += 1  # update metadata counter
                already_has += 1       # update image counter

                print(f"✅ [{idi}] Image {img_id} (similarity = {score:.2f}) has been saved in [{query_dir}] successfully!")
                print(f"📄 Checking metadata/downloaded images: {downloaded_meta+1}/{already_has+1}")

            except Exception as e:
                print(f"❌ Failed to save image {img_id}: {e}")
            time.sleep(0.1)  # optional rate-limit protection         

        # Report per page
        already_has = len(os.listdir(query_dir))
        downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0
        print(f"📌 Page {page} completed.")
        print(f"➡️  Progress: {already_has}/{target_count}")
        print(f"📄 Checking metadata/downloaded images: {downloaded_meta}/{already_has}")

    # Summary
    already_has = len(os.listdir(query_dir))
    downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0
    print("\n🎯 FINAL RESULT")
    print(f"Images already in folder {query}: {already_has_not_change}")
    print(f"Downloaded new images: {saved_img}")
    print(f"Progress for {query}: {already_has}/{target_count} images.")
    print(f"Metadata entries in file: {downloaded_meta}")
    print("Done!" if already_has >= target_count else "No more relevant images available.")
