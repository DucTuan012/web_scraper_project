import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def fetch_gold_prices():
    """
    Lấy giá vàng từ trang web Bảo Tín Minh Châu.
    """
    # URL mục tiêu
    url = "https://btmc.vn/"
    
    # Thêm headers để giả lập trình duyệt
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Gửi yêu cầu HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Báo lỗi nếu request hỏng
        
        # Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các hàng trong bảng giá
        # (Sau khi kiểm tra, tôi thấy btmc.vn dùng <tbody> với id="Gia-vang-SJC")
        data_rows = soup.find(id="Gia-vang-SJC").find_all('tr')
        
        gold_data = []
        
        for row in data_rows:
            cols = row.find_all('td')
            if len(cols) >= 3: # Đảm bảo hàng có đủ cột
                loai_vang = cols[0].text.strip()
                gia_mua = cols[1].text.strip()
                gia_ban = cols[2].text.strip()
                
                if "SJC" in loai_vang: # Chỉ lấy SJC cho ví dụ
                    print(f"Loại: {loai_vang} | Mua: {gia_mua} | Bán: {gia_ban}")
                    gold_data.append({
                        'Loại Vàng': loai_vang,
                        'Giá Mua': gia_mua,
                        'Giá Bán': gia_ban,
                        'Thời gian': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Lưu vào DataFrame của Pandas
        df = pd.DataFrame(gold_data)
        
        # Lưu ra file CSV trong thư mục data
        df.to_csv('data/gold_prices.csv', index=False, mode='a', header=not pd.io.common.file_exists('data/gold_prices.csv'))
        
        print("Đã lấy và lưu giá vàng thành công!")
        return df

    except requests.RequestException as e:
        print(f"Lỗi khi tải trang: {e}")
    except AttributeError as e:
        print(f"Lỗi khi tìm thẻ HTML (có thể trang web đã thay đổi): {e}")
    except Exception as e:
        print(f"Đã xảy ra lỗi không xác định: {e}")

if __name__ == "__main__":
    fetch_gold_prices()