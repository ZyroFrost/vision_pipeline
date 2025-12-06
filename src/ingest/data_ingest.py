from pathlib import Path # Thư viện pathlib để làm việc với đường dẫn hệ thống

# --- Đường dẫn thư mục gốc (ROOT = .../food_vision_ai) ---
ROOT = Path(__file__).resolve().parents[2]  # vì file đang nằm ở ingest/
# __file__ là biến đặc biệt mà Python tự tạo, chứa đường dẫn của file đang chạy
#.resolve() – chuyển thành đường dẫn tuyệt đối
#.parents[2] – đi ngược lên thư mục cha (tức là thư mục gốc của dự án) - [2] -> đi lên 2 cấp
print(f"📂 Thư mục gốc của dự án: {ROOT}")

# --- Đường dẫn lưu dữ liệu ---
RAW_DIR = ROOT / "data" / "raw"
print(f"📂 Thư mục lưu dữ liệu thô: {RAW_DIR}")

META_DIR = ROOT / "data" / "metadata"
print(f"📂 Thư mục lưu metadata: {META_DIR}")

PRO_DIR = ROOT / "data" / "processed"
print(f"📂 Thư mục lưu dữ liệu đã xử lý: {PRO_DIR}")

# --- Tạo thư mục nếu chưa có ---
RAW_DIR.mkdir(parents=True, exist_ok=True) # mkdir = make directory (tạo thư mục), parents=True (tạo cả thư mục cha nếu chưa có)
META_DIR.mkdir(parents=True, exist_ok=True) # exist_ok=True (không báo lỗi nếu thư mục đã tồn tại)
PRO_DIR.mkdir(parents=True, exist_ok=True)

print("✅ Thư mục dữ liệu đã sẵn sàng!")