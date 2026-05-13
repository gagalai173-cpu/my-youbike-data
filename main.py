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
        # 重新嚴格定義欄位順序
        headers = ['更新時間', '站名', '總可借車數', '可歸還空位數', '一般車數量', '電輔車數量', '站點UID']
        
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(headers)

        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 擷取數據 (補強細節抓取邏輯)
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    
                    # 處理某些站點可能沒有 Detail 的情況
                    detail = s.get('AvailableReturnBikesDetail', {})
                    # 如果 Detail 是空的，我們保險起見把 total 歸類到一般車
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    if reg == 0 and ebike == 0 and total > 0:
                        reg = total # 避免出現總數 53 但明細都是 0 的怪現象
                    
                    # 嚴格對齊 headers 的順序寫入
                    writer.writerow([now, name, total, spaces, reg, ebike, uid])
                    print(f"✅ 成功錄入：{name}")

except Exception as e:
    print(f"⚠️ 錯誤: {e}")
