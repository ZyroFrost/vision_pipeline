import os
import requests # thư viện gửi yêu cầu HTTP
import time # thư viện làm việc với thời gian (giới hạn tốc độ gọi API)
import pandas as pd # thư viện xử lý dữ liệu dạng bảng
from pathlib import Path # thư viện làm việc với đường dẫn hệ thống
from datetime import datetime
from dotenv import load_dotenv  # dùng để đọc API key từ file .env
from clip_filter import is_image_relevant # hàm kiểm tra tính liên quan của ảnh, tạo ở clip_filter.py

# Tải biến môi trường từ file .env (chứa access key của Unsplash)
load_dotenv()

# Lấy access key từ biến môi trường
ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY") # Biến môi trường UNSPLASH_ACCESS_KEY phải được thiết lập trong file .env

if ACCESS_KEY is None:
    raise ValueError("❌ Vui lòng thiết lập biến môi trường UNSPLASH_ACCESS_KEY trong file .env")

# Định nghĩa đường dẫn. Tạo lại để unsplash_downloader.py có thể chạy độc lập (khi crawl ảnh nhiều lần, hoặc deploy trên server riêng)
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
META_DIR = ROOT / "data" / "metadata"
META_DIR.mkdir(parents=True, exist_ok=True) # make folder if not exist
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Hàm tải ảnh từ Unsplash
def download_image(query: str, page: int, per_page: int = 30):
    """
    Gọi API Unsplash để lấy ảnh theo từ khóa (query)
    :param query: Từ khóa tìm kiếm (vd: 'pizza', 'burger')
    :param count: Số ảnh muốn lấy
    :return: Danh sách dict chứa thông tin ảnh
    """
    url = "https://api.unsplash.com/search/photos" # Endpoint API Unsplash để tìm kiếm ảnh
    params = {
        "query": query, # Từ khóa tìm kiếm
        "page": page, # trang ảnh
        "per_page": per_page, # số ảnh tối đa mỗi trang (Unsplash giới hạn tối đa 30)
        "content_filter": "high",  # lọc ảnh liên quan hơn
        "client_id": ACCESS_KEY # Access key để xác thực
    }

    response = requests.get(url, params=params) # Gửi yêu cầu GET đến API Unsplash
    if response.status_code != 200: # Kiểm tra mã trạng thái HTTP (trạng thái 200 nghĩa là thành công)
        raise Exception(f"❌ Lỗi khi gọi API Unsplash: {response.status_code} - {response.text}") # Nếu không thành công, in lỗi
    data = response.json()
    return data.get("results", [])

# Kiểm tra thử API Unsplash hoạt động
if __name__ == "__main__":
    query = "sushi" # Chủ đề ảnh muốn tải
    total_count = 1000 # Số ảnh muốn tải
    max_pages = 1000   # Unsplash cho phép tối đa 1000 trang
    per_page = 30  # Số ảnh mỗi trang, tối đa 30 API là 30 nên set 30 luôn
    batch_size = 30  # Unsplash giới hạn mỗi lần gọi API chỉ được lấy tối đa 30 ảnh

    # num_batches = math.ceil(total_count / batch_size) # Giới hạn số lần gọi API (mỗi lần lấy 30 ảnh)
    # Không cần biến này nữa vì filter luôn mỗi batch -> ko thể đếm đc chính xác vòng lặp sẽ chạy bao nhiêu batches vì dựa vào ảnh đã down trong folder

    metadata_list = [] # Danh sách lưu metadata
    meta_path = META_DIR / f"{query}_metadata.csv"
    query_dir = RAW_DIR / query # Tạo thư mục con cho từng từ khóa
    query_dir.mkdir(parents=True, exist_ok=True) # Tạo thư mục nếu chưa có

    already_downloaded = len(os.listdir(RAW_DIR / query)) # Đếm số ảnh đã tải trước đó trong forder
    downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0 # Đếm số metadata đã lưu trước đó
    attempt = 0 # Biến đếm số lần gọi API
    total_downloaded = 0
    passed = 0
    failed = 0
    duplicates = 0

    print(f"📸 Đang tải chủ đề: {query}")
    print(f"📂 Đã có sẵn {already_downloaded} ảnh trong folder.")
    print(f"📂 Đã có sẵn {downloaded_meta} metadata trong file.")
    print(f"🎯 Mục tiêu: Tải tổng cộng {total_count} ảnh hợp lệ trong folder.")
    print(f"🔄 Bắt đầu tải {total_count-already_downloaded} ảnh ({batch_size} ảnh mỗi đợt)...")

    # Bắt đầu vòng lặp tải ảnh
    for page in range(1, max_pages + 1):
        already_downloaded = len(os.listdir(RAW_DIR / query)) # Cập nhật lại số ảnh đã tải
        downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0 # Cập nhật lại số metadata đã lưu
        if already_downloaded >= total_count:
            break  # Đã tải đủ số ảnh cần thiết, dừng lại

        attempt += 1 # Tăng biến đếm số lần gọi API
        remaining = total_count - already_downloaded # Số ảnh còn lại cần tải
        print(f"\n📦 Đợt {attempt}: Gọi API lấy {batch_size} ảnh (thiếu {remaining})...")
        print(f"📄 Trang {page}/{max_pages} — Đang tải {per_page} ảnh...")

        try:
            batch = download_image(query, page=page, per_page=per_page) # Gọi hàm API để lấy ảnh
        except Exception as e:
            print(f"⚠️ Lỗi API (đợt {attempt}): {e}")
            time.sleep(3)
            continue

        if not batch: 
            print("⚠️ Hết ảnh hoặc không còn kết quả mới, dừng lại.")
            break # Nếu không còn ảnh trả về từ API

        print(f"➡️  Nhận {len(batch)} metadata từ API. Bắt đầu lọc & lưu...\n")
        for i, img in enumerate(batch): # Lặp qua từng ảnh trong đợt
            if already_downloaded >= total_count:
                print("✅ Đã tải đủ số ảnh cần thiết, tổng cộng:", already_downloaded)
                break  # Đã tải đủ số ảnh cần thiết, dừng lại
            
            img_url = img['urls']['regular'] # Lấy URL ảnh kích thước thường
            img_id = img['id'] # Lấy ID ảnh
            img_ext = 'jpg' # Định dạng ảnh
            img_filename = f"{query}_{img_id}.{img_ext}" # Tên file ảnh
            img_path = RAW_DIR / query / img_filename # Đường dẫn lưu ảnh, thêm query để phân loại theo thư mục

            if img_path.exists(): # Kiểm tra nếu ảnh đã tồn tại trong thư mục
                duplicates += 1
                print(f"⚠️  Ảnh thứ {i+1} ({img_id}) đã tồn tại, bỏ qua.")
                continue  # Bỏ qua ảnh đã tồn tại

            # Tải và lưu ảnh (thêm bước kiểm tra tính liên quan của ảnh với từ khóa bằng CLIP)
            ok, score = is_image_relevant(img_url, query)  # Kiểm tra tính liên quan của ảnh với từ khóa
            if not ok:
                failed += 1
                print(f"🚫 Ảnh thứ {i+1} ({img_id}) không phù hợp với chủ đề '{query}' (điểm tương đồng = {score:.2f}), bỏ qua.")
                continue  # Bỏ qua ảnh không phù hợp
            passed += 1

            # Tải ảnh về và lưu
            try:
                img_data = requests.get(img_url, timeout=10).content # Gửi yêu cầu tải ảnh với timeout
                with open(img_path, 'wb') as f: # Mở file để ghi ảnh
                    f.write(img_data) 

                # Save metadata vào list
                metadata_list.append({
                    "id": img_id,
                    "query": query,
                    "filename": img_filename,
                    "url": img_url,
                    "downloaded_at": datetime.now().isoformat() # Thời gian tải ảnh
                    })
                
                print(f"✅ Ảnh thứ {i+1} ({img_id}) đã được lưu tại {img_path} (điểm tương đồng = {score:.2f})")

            except Exception as e:
                print(f"❌ Lỗi khi tải ảnh {img_id}: {e}")
                continue
            
        # Lưu metadata sau mỗi đợt
        if metadata_list:
            df = pd.DataFrame(metadata_list)
            if meta_path.exists():
                df.to_csv(meta_path, mode='a', header=False, index=False) #  a = append, ghi dữ liệu vào cuối file
            else:
                df.to_csv(meta_path, index=False) # Lưu mới nếu file chưa tồn tại
            metadata_list = []   # <--- THÊM DÒNG NÀY để reset danh sách sau khi lưu

        already_downloaded = len(os.listdir(RAW_DIR / query))
        downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0
        print(f"📊 Đợt {attempt} hoàn tất. Tổng ảnh hiện có: {already_downloaded}")
        print(f"💾 Kiểm tra đồng bộ metadata và ảnh: tổng cộng có {downloaded_meta} metadata/{already_downloaded} ảnh")
        time.sleep(4)

    already_downloaded = len(os.listdir(RAW_DIR / query)) #
    downloaded_meta = len(pd.read_csv(meta_path)) if meta_path.exists() else 0
    print(f"\n🎯 Hoàn tất! Đã tải đủ {already_downloaded}/{total_count} ảnh hợp lệ sau {attempt} lần gọi API.")
    print(f"\n💾 Kiểm tra đồng bộ metadata và ảnh: tổng cộng có {downloaded_meta} metadata/{already_downloaded} ảnh")

    # Tổng kết thực tế
    print(f"\n📊 Tổng kết:")
    print(f"   • Tổng ảnh đã xử lý: {passed + failed + duplicates}")
    print(f"   • Ảnh pass CLIP và ko trùng: {passed}")
    print(f"   • Ảnh bị trùng: {duplicates}")