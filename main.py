import urllib.request
import json
import csv
import os
from datetime import datetime # 修正點：確保載入時間模組

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
        # 欄位名稱重新定義，確保與 App 邏輯一致
        headers = ['紀錄時間(台北)', '站名', '可借車輛合計', '一般車', '電輔車', '空車位(可還)', '站點UID']
        
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(headers)

        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 強制設定時區為台北 (UTC+8)
            tz = timezone(timedelta(hours=8))
            now_tw = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    
                    # 重新對應 TDX 欄位
                    # AvailableReturnBikes = 現場有的車 = 可借
                    can_borrow = s.get('AvailableReturnBikes', 0)
                    # AvailableRentSpaces = 現場空位 = 可還
                    can_return = s.get('AvailableRentSpaces', 0)
                    
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    # 邏輯補正：若明細為 0 但總數有值，歸類為一般車
                    if reg == 0 and ebike == 0 and can_borrow > 0:
                        reg = can_borrow
                    
                    writer.writerow([now_tw, name, can_borrow, reg, ebike, can_return, uid])
                    print(f"✅ 紀錄成功：{name} (可借:{can_borrow}, 可還:{can_return})")

except Exception as e:
    print(f"⚠️ 錯誤: {e}")
