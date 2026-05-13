import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

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
                csv.writer(f).writerow(['更新時間', '站點名稱', '可借總數', '可還空位', '一般車', '電輔車', '原始ID'])

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                # 取得所有可能的識別標籤
                uid = str(s.get('StationUID', ''))
                sid = str(s.get('StationID', ''))
                # 即時動態 API 的名稱有時在不同層級，我們全都試試看
                name = s.get('StationName', {}).get('Zh_tw', '') or s.get('sna', '')
                
                # --- 核心邏輯：只要符合以下任一條件就抓取 ---
                # 1. ID 包含 501201083 或 501201082
                # 2. 名稱包含 "楠梓高中"
                is_target = any(target_id in uid or target_id in sid for target_id in ['501201083', '501201082'])
                is_name_match = "楠梓高中" in name
                
                if is_target or is_name_match:
                    # 如果名稱是空的，就暫時用 ID 代替
                    display_name = name if name else f"未知站點({uid})"
                    update_time = s.get('UpdateTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    writer.writerow([update_time, display_name, total, spaces, reg, ebike, uid])
                    print(f"✅ 成功命中: {display_name} (ID: {uid})")
                    found_count += 1
        
        print(f"🏁 任務結束。全高雄 1400+ 站掃描完畢，共抓到 {found_count} 筆目標。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
