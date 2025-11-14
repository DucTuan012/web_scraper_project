# scrape_gold.py
import json
import requests
from bs4 import BeautifulSoup

# File để lưu trữ giá
JSON_FILE = 'gold_price.json'

def get_last_price():
    """Đọc giá từ file JSON."""
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
            # Đảm bảo file có dữ liệu
            if data and 'buy' in data:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu file không tồn tại hoặc lỗi, trả về giá trị 0
        pass
    return {'buy': 0, 'sell': 0}

def save_new_price(new_price_data):
    """Lưu giá mới vào file JSON."""
    with open(JSON_FILE, 'w') as f:
        json.dump(new_price_data, f, indent=4)

def scrape_current_price():
    """
    !!! PHẦN QUAN TRỌNG NHẤT !!!
    BẠN CẦN THAY THẾ PHẦN NÀY BẰNG LOGIC SCRAPE CỦA BẠN
    Hàm này phải trả về một dictionary, ví dụ: {'buy': 70000000, 'sell': 71000000}
    """
    
    # --- BẮT ĐẦU VÍ DỤ MẪU (HÃY XÓA VÀ THAY THẾ) ---
    # Đây chỉ là ví dụ, bạn phải dùng code scrape thật của bạn
    # Ví dụ:
    # url = "https://example-gold-site.com"
    # headers = {'User-Agent': 'Mozilla/5.0...'}
    # response = requests.get(url, headers=headers)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # 
    # # Giả sử bạn tìm được giá mua và bán (chuyển về số nguyên)
    # price_buy_str = soup.find(id='gia_mua').text.replace('.', '')
    # price_sell_str = soup.find(id='gia_ban').text.replace('.', '')
    # new_buy = int(price_buy_str)
    # new_sell = int(price_sell_str)
    # 
    # return {'buy': new_buy, 'sell': new_sell}
    # --- KẾT THÚC VÍ DỤ MẪU ---

    # Nếu bạn chưa có code, hãy dùng code giả lập này để test
    # Nó sẽ tạo ra giá ngẫu nhiên để bạn thấy sự thay đổi
    import random
    print("ĐANG SỬ DỤNG CODE GIẢ LẬP ĐỂ TEST")
    new_buy_price = 70000000 + random.randint(-500000, 500000)
    new_sell_price = 71000000 + random.randint(-500000, 500000)
    return {'buy': new_buy_price, 'sell': new_sell_price}


def compare_and_print(old_price, new_price, key):
    """So sánh và in ra thay đổi."""
    old = old_price[key]
    new = new_price[key]
    change = new - old
    
    if old == 0: # Lần chạy đầu tiên
        print(f"Giá {key} khởi tạo: {new:,.0f} VND")
    elif change > 0:
        print(f"Giá {key}: {new:,.0f} VND (Tăng {change:,.0f} VND)")
    elif change < 0:
        print(f"Giá {key}: {new:,.0f} VND (Giảm {abs(change):,.0f} VND)")
    else:
        print(f"Giá {key}: {new:,.0f} VND (Không đổi)")

# --- Luồng chạy chính ---
if __name__ == "__main__":
    print("--- Bắt đầu kiểm tra giá vàng ---")
    
    # 1. Đọc giá cũ
    last_price = get_last_price()
    
    # 2. Scrape giá mới
    current_price = scrape_current_price()
    
    # 3. So sánh và In
    compare_and_print(last_price, current_price, 'buy')
    compare_and_print(last_price, current_price, 'sell')
    
    # 4. Lưu giá mới
    save_new_price(current_price)
    
    print("--- Hoàn tất ---")