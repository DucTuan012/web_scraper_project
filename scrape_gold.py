import requests
from bs4 import BeautifulSoup
import json
import os
import time

URL = "https://btmc.vn/"
JSON_FILE = 'gold_data.json' 
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_price_to_int(price_str):
    if not isinstance(price_str, str):
        return 0
    
    price_str = price_str.strip().lower()
    
    if "liên hệ" in price_str or not price_str:
        return 0
    
    cleaned_str = "".join(filter(str.isdigit, price_str))
    
    try:
        return int(cleaned_str)
    except ValueError:
        return 0

def get_last_data(json_file):

    if not os.path.exists(json_file):
        return {'last_updated': 'Chưa có', 'prices': {}}
        
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'last_updated' in data and 'prices' in data:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {'last_updated': 'Chưa có', 'prices': {}}

def save_new_data(json_file, new_data):
    directory = os.path.dirname(json_file)
    if directory and not os.path.exists(directory):
        print(f"Tạo thư mục: {directory}")
        os.makedirs(directory)
        
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

def fetch_gold_prices():
    print(f"Đang đọc giá cũ từ: {JSON_FILE}...")
    last_data = get_last_data(JSON_FILE)
    last_update_time = last_data['last_updated']
    last_prices = last_data['prices'] 
    
    print(f"Đang kết nối tới: {URL}...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'lxml') 

        new_update_time_str = "Không tìm thấy"
        update_time_element = soup.find('span', class_='mr-3')
        if update_time_element:
            full_text = update_time_element.text.strip()
            if "Cập nhật lúc" in full_text:
                new_update_time_str = full_text.replace("Cập nhật lúc", "").strip()
        
        print(f"Thời gian cập nhật cũ (từ file): {last_update_time}")
        print(f"Thời gian cập nhật mới (từ web): {new_update_time_str}")

        if new_update_time_str == last_update_time:
            print("Giá không thay đổi (thời gian cập nhật giống hệt lần trước). Bỏ qua.")
            print("--- Hoàn tất ---")
            return
        
        print("Thời gian cập nhật đã thay đổi, bắt đầu lấy giá mới...")

        gold_table = soup.find('table', class_='bd_price_home')
        if not gold_table:
            print("LỖI: Không tìm thấy bảng giá (class 'bd_price_home').")
            return

        data_rows = gold_table.find_all('tr')
        current_prices_dict = {} 
        
        print("\n--- SO SÁNH CHI TIẾT GIÁ ---")
        for row in data_rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue 

            loai_vang = cols[1].text.strip()
            gia_mua_str = cols[3].text.strip()
            gia_ban_str = cols[4].text.strip()

            if not loai_vang:
                continue

            gia_mua_num = clean_price_to_int(gia_mua_str)
            gia_ban_num = clean_price_to_int(gia_ban_str)
            
            old_price_data = last_prices.get(loai_vang, {})
            last_mua = old_price_data.get('buy_num', 0)
            
            change = 0
            change_str = "--- (Mới)"
            if gia_mua_num != 0 and last_mua != 0:
                change = gia_mua_num - last_mua
            
            if change > 0:
                change_str = f"TĂNG +{change:,.0f}"
            elif change < 0:
                change_str = f"GIẢM {change:,.0f}"
            elif change == 0 and last_mua != 0:
                 change_str = "Không đổi"

            print(f" {loai_vang} | Mua: {gia_mua_str} | Thay đổi: {change_str}")

            current_prices_dict[loai_vang] = {
                'buy_str': gia_mua_str,
                'sell_str': gia_ban_str,
                'buy_num': gia_mua_num,
                'sell_num': gia_ban_num
            }

        if not current_prices_dict:
            print("Tìm thấy bảng nhưng không xử lý được dữ liệu nào.")
            return

        new_data_to_save = {
            'last_updated': new_update_time_str,
            'prices': current_prices_dict
        }
        
        save_new_data(JSON_FILE, new_data_to_save)
        print(f"\nĐã cập nhật và ghi đè file: {JSON_FILE}")
        print("--- Hoàn tất ---")

    except requests.RequestException as e:
        print(f"Lỗi khi tải trang: {e}")
    except Exception as e:
        print(f"Đã xảy ra lỗi không xác định: {e}")

if __name__ == "__main__":
    fetch_gold_prices()