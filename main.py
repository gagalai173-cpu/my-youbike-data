import urllib.request
import json
import csv
import os
from datetime import datetime, timedelta, timezone

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

target_ids = {
    'KHH501210027': 'YouBike2.0_楠梓高中',
    'KHH501210124': 'YouBike2.0_楠梓高中(土庫六路側)'
}

def get_token():
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    params = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    try:
        req = urllib.request.Request(auth_url, data=params.encode())
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())['access_token']
    except:
        return None

try:
    token = get_token()
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        # 標題完全比照 App 顯示名稱
        headers = ['紀錄時間(台北)', '站名', '可借總數(車)', '一般車', '電輔車', '可停空位(柱)', '站點UID']
        
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(headers)

        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            tz = timezone(timedelta(hours=8))
            now_tw = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    
                    # --- 核心邏輯反轉修正 ---
                    # 根據老師實測 App 與 API 對比：
                    # 這次我們發現高雄 TDX 欄位定義如下：
                    can_stop_spaces = s.get('AvailableReturnBikes', 0) # 53 應該是空位
                    can_borrow_total = s.get('AvailableRentSpaces', 0) # 8 應該是可借總數
                    
                    detail = s.get('AvailableReturnBikesDetail', {}) # 注意：明細通常跟著「車輛」走
                    # 如果明細還是抓不到，我們從總數推算
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    # 再次對齊：如果總數有車但明細是0，補到一般車
                    if reg == 0 and ebike == 0 and can_borrow_total > 0:
                        reg = can_borrow_total

                    writer.writerow([now_tw, name, can_borrow_total, reg, ebike, can_stop_spaces, uid])
                    print(f"✅ 修正錄入：{name} [可借:{can_borrow_total} (一般{reg}/電輔{ebike}), 可停:{can_stop_spaces}]")

except Exception as e:
    print(f"⚠️ 錯誤: {e}")
