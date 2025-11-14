import json
import requests
from bs4 import BeautifulSoup
import re

# File để lưu trữ giá
JSON_FILE = 'gold_price.json'

def get_last_price():
    """Đọc giá từ file JSON."""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
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
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_price_data, f, indent=4, ensure_ascii=False)

def clean_price(price_str):
    """Xóa ký tự không phải số (như ,) và chuyển thành số nguyên."""
    # Xóa tất cả các ký tự không phải là số
    cleaned_str = re.sub(r'[^\d]', '', price_str)
    try:
        return int(cleaned_str)
    except ValueError:
        print(f"Lỗi: Không thể chuyển đổi '{price_str}' thành số.")
        return 0

def scrape_current_price():
    """
    --- PHIÊN BẢN CHÍNH THỨC ---
    Scrape giá vàng SJC 1L, 10L từ website giavang.org
    """
    url = "https://giavang.org/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Bắt đầu scrape từ {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Báo lỗi nếu request thất bại (ví dụ: 404, 500)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các hàng <tr> trong bảng
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            # Tìm hàng có chứa "SJC 1L, 10L"
            if cells and "SJC 1L, 10L" in cells[0].get_text():
                price_buy_str = cells[1].get_text()
                price_sell_str = cells[2].get_text()
                
                print(f"Tìm thấy giá thô: Mua='{price_buy_str}', Bán='{price_sell_str}'")
                
                # Làm sạch giá
                new_buy = clean_price(price_buy_str)
                new_sell = clean_price(price_sell_str)
                
                if new_buy > 0 and new_sell > 0:
                    return {'buy': new_buy, 'sell': new_sell}
                else:
                    print("Lỗi: Không thể làm sạch giá về số dương.")
                    return None

        print("Lỗi: Không tìm thấy hàng 'SJC 1L, 10L' trên trang.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi request đến website: {e}")
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi scrape: {e}")
        return None

def compare_and_print(old_price, new_price, key):
    """So sánh và in ra thay đổi."""
    old = old_price.get(key, 0) # Dùng .get để tránh lỗi nếu key không tồn tại
    new = new_price.get(key, 0)
    
    if old == 0: # Lần chạy đầu tiên
        print(f"Giá {key.upper()} khởi tạo: {new:,.0f} VND")
    elif new == 0:
        print(f"Lỗi: Không lấy được giá {key.upper()} mới.")
    else:
        change = new - old
        if change > 0:
            print(f"Giá {key.upper()}: {new:,.0f} VND (Tăng +{change:,.0f} VND)")
        elif change < 0:
            print(f"Giá {key.upper()}: {new:,.0f} VND (Giảm {change:,.0f} VND)")
        else:
            print(f"Giá {key.upper()}: {new:,.0f} VND (Không đổi)")

# --- Luồng chạy chính ---
if __name__ == "__main__":
    print("--- Bắt đầu kiểm tra giá vàng (Phiên bản chính thức) ---")
    
    # 1. Đọc giá cũ
    last_price = get_last_price()
    print(f"Giá cũ (từ file): Mua={last_price['buy']}, Bán={last_price['sell']}")
    
    # 2. Scrape giá mới
    current_price = scrape_current_price()
    
    # 3. So sánh và In
    if current_price:
        print("--- So sánh giá ---")
        compare_and_print(last_price, current_price, 'buy')
        compare_and_print(last_price, current_price, 'sell')
        
        # 4. Lưu giá mới
        save_new_price(current_price)
        print(f"Đã lưu giá mới vào {JSON_FILE}")
    else:
        print("Không thể lấy được giá mới. Bỏ qua lần cập nhật này.")
    
    print("--- Hoàn tất ---")