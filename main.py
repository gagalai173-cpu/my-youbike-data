import urllib.request
import json
import csv
import os
from datetime import datetime # 修正點：確保載入時間模組

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 正確的 UID 對照表
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
        # 重新定義整齊的標題列
        headers = ['紀錄時間', '站名', '可借總數', '可還空位', '一般車數量', '電輔車數量', '站點UID']
        
        # 如果檔案不存在，建立新檔並寫入標題
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(headers)

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 擷取數據
                    available_bikes = s.get('AvailableReturnBikes', 0)
                    available_spaces = s.get('AvailableRentSpaces', 0)
                    detail = s.get('AvailableReturnBikesDetail', {})
                    general_bikes = detail.get('GeneralBikes', 0)
                    electric_bikes = detail.get('ElectricBikes', 0)
                    
                    # 按照標題順序寫入！
                    writer.writerow([now, name, available_bikes, available_spaces, general_bikes, electric_bikes, uid])
                    print(f"✅ 成功錄入資料：{name}")
                    found_count += 1
        
        print(f"🏁 任務完成！已成功對齊並存入 {found_count} 筆資料。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
