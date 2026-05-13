import urllib.request
import json
import csv
import os
from datetime import datetime

# --- 請在此填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

file_name = 'youbike_log.csv'
if "楠梓高中" in name:

def get_token():
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    # 向 TDX 伺服器申請限時通行證
    params = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    req = urllib.request.Request(auth_url, data=params.encode())
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode())['access_token']

# 初始化 CSV 檔案標題
if not os.path.exists(file_name):
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerow(['時間', '站名', '可借車輛', '可還空位'])

try:
    # 1. 取得認證 Token
    token = get_token()
    
    # 2. 使用 Token 請求資料
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        found = False
        for s in data:
            name = s.get('StationName', {}).get('Zh_tw', '')
            if target_name in name:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                bike = s.get('AvailableReturnBikes')
                space = s.get('AvailableRentSpaces')
                
                # 寫入資料
                with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                    csv.writer(f).writerow([now, name, bike, space])
                
                print(f"✅ 認證擷取成功: {name} (可借:{bike})")
                found = True
                break
        
        if not found:
            print(f"❌ 找不到站點: {target_name}")

except Exception as e:
    print(f"⚠️ 執行發生錯誤: {e}")
