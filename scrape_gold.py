import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# --- CÁC BIẾN CẤU HÌNH ---
URL = "https://btmc.vn/"
SNAPSHOT_FILE = 'data/gold_snapshot.csv' # File này luôn bị ghi đè (mode='w')
HISTORY_FILE = 'data/gold_history.csv'   # File này lưu lịch sử (mode='a')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_price_to_int(price_str):
    """
    Chuyển một chuỗi giá (ví dụ "15,120" hoặc "Liên hệ") thành số int.
    Trả về 0 nếu không phải là số.
    """
    if not isinstance(price_str, str):
        return 0
    
    price_str = price_str.strip().lower()
    
    if "liên hệ" in price_str or not price_str:
        return 0
    
    # Xóa các ký tự không phải số
    cleaned_str = "".join(filter(str.isdigit, price_str))
    
    try:
        return int(cleaned_str)
    except ValueError:
        return 0

def get_last_prices(snapshot_file):
    """
    Đọc file snapshot từ LẦN CHẠY TRƯỚC để lấy giá cũ.
    Trả về một dictionary, ví dụ: {'VÀNG MIẾNG SJC': 15120}
    """
    last_prices = {}
    if not os.path.exists(snapshot_file):
        return last_prices # File không tồn tại, trả về rỗng

    try:
        df_last = pd.read_csv(snapshot_file)
        # Tạo một dict từ 2 cột 'Loại Vàng' và 'Giá Mua (Số)'
        # Nếu file snapshot cũ chưa có cột 'Giá Mua (Số)',
        # chúng ta sẽ dùng 'Giá Mua' và clean nó.
        
        if 'Giá Mua (Số)' in df_last.columns:
             last_prices = dict(zip(df_last['Loại Vàng'], df_last['Giá Mua (Số)']))
        elif 'Giá Mua' in df_last.columns:
             print("Đang đọc snapshot cũ (không có cột 'Giá Mua (Số)')...")
             for _, row in df_last.iterrows():
                 last_prices[row['Loại Vàng']] = clean_price_to_int(row['Giá Mua'])
        
        return last_prices
    except pd.errors.EmptyDataError:
        print("File snapshot rỗng, không có giá cũ.")
        return {}
    except Exception as e:
        print(f"Lỗi khi đọc file snapshot cũ: {e}")
        return {}


def fetch_gold_prices():
    """
    Hàm chính để scrape, xử lý và lưu dữ liệu.
    """
    print(f"Đang đọc giá cũ từ: {SNAPSHOT_FILE}...")
    last_prices_map = get_last_prices(SNAPSHOT_FILE)
    
    print(f"Đang kết nối tới: {URL}...")
    try:
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'lxml') # Dùng 'lxml' cho ổn định

        # 1. Lấy thời gian cập nhật
        update_time_str = "Không tìm thấy"
        update_time_element = soup.find('span', class_='mr-3')
        if update_time_element:
            full_text = update_time_element.text.strip()
            if "Cập nhật lúc" in full_text:
                update_time_str = full_text.replace("Cập nhật lúc", "").strip()
        print(f"Thời gian cập nhật (từ Website): {update_time_str}")

        # 2. Lấy bảng giá
        gold_table = soup.find('table', class_='bd_price_home')
        if not gold_table:
            print("LỖI: Không tìm thấy bảng giá (class 'bd_price_home' có thể đã thay đổi).")
            return

        data_rows = gold_table.find_all('tr')
        processed_data = []
        scrape_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        for row in data_rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue # Bỏ qua hàng không hợp lệ

            loai_vang = cols[1].text.strip()
            gia_mua_str = cols[3].text.strip()
            gia_ban_str = cols[4].text.strip()

            if not loai_vang: # Bỏ qua hàng không có tên
                continue

            # 3. Xử lý số và so sánh
            gia_mua_num = clean_price_to_int(gia_mua_str)
            gia_ban_num = clean_price_to_int(gia_ban_str)
            
            # Lấy giá cũ từ dict
            last_mua = last_prices_map.get(loai_vang, 0)
            
            change = 0
            change_str = "---"
            if gia_mua_num != 0 and last_mua != 0:
                change = gia_mua_num - last_mua
            
            if change > 0:
                change_str = f"TĂNG +{change}"
            elif change < 0:
                change_str = f"GIẢM {change}"
            
            print(f"[ĐANG LẤY] {loai_vang} | Mua: {gia_mua_str} | Bán: {gia_ban_str} | Thay đổi: {change_str}")

            processed_data.append({
                'Thời gian (Scrape)': scrape_timestamp,
                'Thời gian (Website)': update_time_str,
                'Loại Vàng': loai_vang,
                'Giá Mua': gia_mua_str,
                'Giá Bán': gia_ban_str,
                'Giá Mua (Số)': gia_mua_num,
                'Giá Bán (Số)': gia_ban_num,
                'Thay đổi (Mua)': change
            })

        if not processed_data:
            print("Tìm thấy bảng nhưng không xử lý được dữ liệu nào.")
            return

        # 4. Lưu dữ liệu
        df = pd.DataFrame(processed_data)
        
        # Đảm bảo thư mục 'data' tồn tại
        if not os.path.exists('data'):
            os.makedirs('data')

        # Lưu file Snapshot (luôn ghi đè)
        df.to_csv(SNAPSHOT_FILE, index=False, mode='w', header=True, encoding='utf-8-sig')
        print(f"\nĐã ghi đè file snapshot: {SNAPSHOT_FILE}")

        # Lưu file History (ghi nối tiếp)
        # Ghi header nếu file chưa tồn tại
        file_exists = os.path.exists(HISTORY_FILE)
        df.to_csv(HISTORY_FILE, index=False, mode='a', header=not file_exists, encoding='utf-8-sig')
        print(f"Đã cập nhật file lịch sử: {HISTORY_FILE}")

    except requests.RequestException as e:
        print(f"Lỗi khi tải trang: {e}")
    except Exception as e:
        print(f"Đã xảy ra lỗi không xác định: {e}")

if __name__ == "__main__":
    fetch_gold_prices()