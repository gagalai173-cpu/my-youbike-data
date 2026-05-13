import urllib.request
import json
import csv
import os

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 我們的目標關鍵 ID（拿掉前綴，改用包含搜尋更保險）
targets = {
    '501201083': 'YouBike2.0_楠梓高中',
    '501201082': 'YouBike2.0_楠梓高中(土庫六路側)'
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
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(['時間', '站名', '可借', '可還', '一般', '電輔', '原始ID'])

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                # 取得這站的 UID（轉成字串以便搜尋）
                uid = str(s.get('StationUID', ''))
                
                # 檢查這站是否包含我們的目標 ID 數字
                for tid, tname in targets.items():
                    if tid in uid:
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        total = s.get('AvailableReturnBikes', 0)
                        spaces = s.get('AvailableRentSpaces', 0)
                        detail = s.get('AvailableReturnBikesDetail', {})
                        reg = detail.get('GeneralBikes', 0)
                        ebike = detail.get('ElectricBikes', 0)
                        
                        writer.writerow([now, tname, total, spaces, reg, ebike, uid])
                        print(f"🎯 成功鎖定：{tname} (ID: {uid})")
                        found_count += 1
        
        print(f"🏁 掃描完成，共紀錄 {found_count} 站。")

except Exception as e:
    print(f"⚠️ 錯誤: {e}")
