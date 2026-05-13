import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 使用 image_46843d.png 查到的正確 ID
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
    # 即時動態 API
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        # 初始化標題
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(['時間', '站名', '可借總數', '可還空位', '一般車', '電輔車', 'UID'])

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    # 取得時間與數據
                    update_time = s.get('UpdateTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    writer.writerow([update_time, name, total, spaces, reg, ebike, uid])
                    print(f"✅ 成功攔截！ 站名：{name}")
                    found_count += 1
        
        print(f"🏁 任務完成！共成功紀錄 {found_count} 筆數據至 CSV。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
