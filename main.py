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
    # 核心修正：改用 v3 版本，這通常是目前最穩定的來源
    url = "https://tdx.transportdata.tw/api/basic/v3/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        headers = ['紀錄時間(台北)', '站名', '可借總數', '一般車', '電輔車', '可停空位', '站點UID']
        
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
                    
                    # V3 的欄位定義更直覺一點
                    # 可借總數
                    total = s.get('AvailableReturnBikes', 0)
                    # 可停空位
                    spaces = s.get('AvailableRentSpaces', 0)
                    
                    # 抓取明細
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    # 邏輯保護：若總數有車但明細為 0
                    if (reg + ebike) == 0 and total > 0:
                        reg = total

                    writer.writerow([now_tw, name, total, reg, ebike, spaces, uid])
                    print(f"✅ V3 錄入：{name} (借:{total}, 停:{spaces})")

except Exception as e:
    print(f"⚠️ 錯誤: {e}")
