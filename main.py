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
    'KHH501210124': 'YouBike2.0_楠梓高中(土庫六路側)',
    'KHH501210040': 'YouBike2.0_市立中山高級中學(藍田路側)',
    'KHH501210112': 'YouBike2.0_中山高級中學(藍昌路側)'
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
                    
                    # 依據 image_3bae7b.png 的實測數據對號入座：
                    # 53 是空位，對應的是 AvailableReturnBikes
                    can_stop_spaces = s.get('AvailableReturnBikes', 0) 
                    # 8 是可借總數，對應的是 AvailableRentSpaces
                    can_borrow_total = s.get('AvailableRentSpaces', 0) 
                    
                    # 抓取明細：雖然欄位名稱很怪，但我們把所有細節都翻一遍
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    # 如果明細抓不到，嘗試從另一個可能的地方抓 (有些版本的 API 會放在 Rent 結尾的欄位)
                    if reg == 0 and ebike == 0:
                        rent_detail = s.get('AvailableRentBikesDetail', {})
                        reg = rent_detail.get('GeneralBikes', 0)
                        ebike = rent_detail.get('ElectricBikes', 0)

                    # 數據防護：如果總數有車但明細都是 0，暫時全部歸類為一般車，確保數據邏輯一致
                    if (reg + ebike) == 0 and can_borrow_total > 0:
                        reg = can_borrow_total

                    writer.writerow([now_tw, name, can_borrow_total, reg, ebike, can_stop_spaces, uid])
                    print(f"✅ 數據入庫：{name} (借:{can_borrow_total} / 停:{can_stop_spaces})")

except Exception as e:
    print(f"⚠️ 系統錯誤: {e}")
