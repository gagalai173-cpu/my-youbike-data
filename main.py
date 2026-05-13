import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 這是我們預先查好、絕對不會變的 ID (StationUID)
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
    # 抓取全高雄市的即時動態 (這裡有 1400+ 站)
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        # 初始化檔案與標題
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(['時間', '站名', '可借總數', '可還空位', '一般車', '電輔車'])

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                uid = s.get('StationUID')
                
                # 直接用 ID 比對，不看地址、不看行政區
                if uid in target_map:
                    name = target_map[uid]
                    # 取得即時數值
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    # 取得老師要求的「一般車」與「電輔車」細節
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    # 取得這份資料的更新時間
                    update_time = s.get('UpdateTime', '')
                    
                    writer.writerow([update_time, name, total, spaces, reg, ebike])
                    print(f"✅ 成功攔截資料: {name} (一般:{reg}, 電輔:{ebike})")
                    found_count += 1
        
        print(f"🏁 任務完成，本次共成功紀錄 {found_count} 站。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
