from transformers import CLIPProcessor, CLIPModel # thư viện xử lý và mô hình CLIP để dự đoán ảnh
from PIL import Image # thư viện xử lý ảnh, Pillow, chuyển đổi định dạng ảnh, như RGB
from io import BytesIO # thư viện xử lý luồng byte, json file
import torch # thư viện xử lý tensor và mô hình học sâu
import requests # thư viện gửi yêu cầu HTTP

# Khởi tạo mô hình và bộ xử lý CLIP
print("🔄 Loading CLIP model (openai/clip-vit-base-patch32)...")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32") # Tải mô hình CLIP
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32") # Bộ xử lý CLIP
clip_model.eval()  # Đặt mô hình ở chế độ đánh giá, không huấn luyện, mục đích là để dự đoán

# Hàm kiểm tra tính liên quan của ảnh với đoạn văn bản, 
# threshold là ngưỡng similarity (tùy thuộc từ khóa mà ngưỡng sẽ khác nhau)
def is_image_relevant(img_url: str, query: str, similarity): 
    try:
        headers = {"User-Agent": "Mozilla/5.0"} # Thêm header để tránh bị chặn bởi một số server
        resp = requests.get(img_url, timeout=10, headers=headers)  # Gửi yêu cầu tải ảnh, thêm header và timeout
        resp.raise_for_status()  # Kiểm tra nếu yêu cầu thành công
        image = Image.open(BytesIO(resp.content)).convert("RGB") # Mở ảnh và chuyển đổi sang RGB

        # Xử lý ảnh và đoạn văn bản
        inputs = clip_processor(text=[query], images=image, return_tensors="pt", padding=True)
        with torch.no_grad(): # Vô hiệu hóa tính toán gradient
            outputs = clip_model(**inputs) # Lấy đầu ra từ mô hình CLIP
            image_embeds = outputs.image_embeds # Lấy embedding của ảnh
            text_embeds = outputs.text_embeds # Lấy embedding của đoạn văn bản

        # Tính toán cosine similarity
        cosine_sim = torch.nn.functional.cosine_similarity(image_embeds, text_embeds) # tính cosine similarity giữa 2 embedding
        score = cosine_sim.item() #

        # Kiểm tra nếu similarity vượt qua ngưỡng
        is_relevant = score >= similarity
        return is_relevant, score
    except Exception as e:
        print(f"❌ Lỗi khi tải ảnh từ {img_url}: {e}")
        return False, 0.0

# Test thử hàm trực tiếp, vì dùng kết hợp với unsplash_downloader.py nên không cần test ở đây nữa
'''
if __name__ == "__main__":
    # Thử nghiệm sử dụng hàm is_image_relevant
    test_img_url = "https://images.unsplash.com/photo-1556906918-c3071bd11598?q=80&w=880&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    test_query = "sushi"
    ok, score = is_image_relevant(test_img_url, test_query)

    if ok:
        print(f"Ảnh HỢP LỆ cho chủ đề '{test_query}' (điểm tương đồng = {score:.2f})")
    else:
        print(f"Ảnh KHÔNG PHÙ HỢP (điểm tương đồng = {score:.2f})")
'''