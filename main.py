import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 楠梓高中兩站的唯一 ID
target_ids = {
    'KHH501201083': 'YouBike2.0_楠梓高中',
    'KHH501201082': 'YouBike2.0_楠梓高中(土庫六路側)'
}

def get_token():
    print("Step 1: 正在嘗試取得 TDX 通行證...")
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    params = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    try:
        req = urllib.request.Request(auth_url, data=params.encode())
        with urllib.request.urlopen(req) as res:
            token = json.loads(res.read().decode())['access_token']
            print("🟢 通行證取得成功！")
            return token
    except Exception as e:
        print(f"🔴 通行證取得失敗！請檢查 Client ID/Secret。錯誤原因: {e}")
        return None

try:
    token = get_token()
    if not token:
        exit(1) # 認證失敗就直接結束，不浪費時間

    print("Step 2: 正在連線高雄 YouBike 即時資料庫...")
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        raw_data = res.read().decode()
        data = json.loads(raw_data)
        print(f"🟢 資料連線成功！共抓回 {len(raw_data)} 位元組的資料，包含 {len(data)} 個站點。")
        
        file_name = 'nanzih_bike_data.csv'
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(['時間', '站名', '可借', '可還', '一般', '電輔', 'UID'])

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    writer.writerow([now, name, total, spaces, reg, ebike, uid])
                    print(f"🎯 成功鎖定目標：{name} (一般:{reg}, 電輔:{ebike})")
                    found_count += 1
        
        print(f"Step 3: 掃描完畢，本次共紀錄 {found_count} 筆目標。")

except Exception as e:
    print(f"⚠️ 發生未知錯誤: {e}")
