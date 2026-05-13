import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

file_name = 'nanzih_bike_data.csv'
# 老師指定的兩站精確關鍵字
target_stations = ["楠梓高中", "楠梓高中(土庫六路側)"]

def get_token():
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    params = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    req = urllib.request.Request(auth_url, data=params.encode())
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode())['access_token']

if not os.path.exists(file_name):
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerow(['站名', '更新時間', '總可借', '可歸還', '一般車', '電輔車'])

try:
    token = get_token()
    # 呼叫即時動態 API
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        found_count = 0
        
        # 開啟檔案進行追加紀錄 (mode='a')
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            for s in data:
                name = s.get('StationName', {}).get('Zh_tw', '')
                
                # 檢查這站是不是我們要找的那兩站之一
                if any(target in name for target in target_stations):
                    update_time = s.get('UpdateTime', '')
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    # 擷取細節：注意 TDX 格式，若無細節則預設為 0
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg_bike = detail.get('GeneralBikes', 0)
                    e_bike = detail.get('ElectricBikes', 0)
                    
                    writer.writerow([name, update_time, total, spaces, reg_bike, e_bike])
                    print(f"✅ 成功抓取: {name} (一般:{reg_bike}, 電輔:{e_bike})")
                    found_count += 1
            
        if found_count == 0:
            print("❌ 搜尋完成，但在 1000+ 站點中沒找到包含 '楠梓高中' 的站名。")
            # 小撇步：印出前 5 站看看格式
            print(f"DEBUG: 第一站名稱範例：{data[0].get('StationName', {}).get('Zh_tw', '')}")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
