import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 定義我們要監控的 StationUID 與對應的顯示名稱
target_map = {
    'KHH501201083': 'YouBike2.0_楠梓高中',
    'KHH501201082': 'YouBike2.0_楠梓高中(土庫六路側)'
}

def get_token():
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    params = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    req = urllib.request.Request(auth_url, data=params.encode())
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode())['access_token']

try:
    token = get_token()
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(['時間', '站名', '可借總數', '可還空位', '一般車', '電輔車'])

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                uid = s.get('StationUID')
                
                # 如果這站的 UID 是我們要找的
                if uid in target_map:
                    name = target_map[uid]
                    update_time = s.get('UpdateTime', '')
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    writer.writerow([update_time, name, total, spaces, reg, ebike])
                    print(f"✅ 成功寫入: {name} (ID: {uid})")
                    found_count += 1
        
        print(f"🏁 任務完成，共紀錄 {found_count} 筆資料。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
