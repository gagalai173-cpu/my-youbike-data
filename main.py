import urllib.request
import json
import csv
import os
from datetime import datetime, timedelta, timezone

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

# 楠梓高中正確的實時監測 UID
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
    except Exception as e:
        print(f"🔴 Token 取得失敗: {e}")
        return None

try:
    token = get_token()
    if not token:
        exit(1)

    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        # 欄位重新定義：確保跟老師在 App 上看到的邏輯完全一樣
        headers = ['紀錄時間(台北)', '站名', '可借車輛(合計)', '一般車', '電輔車', '空車位(可還)', 'UID']
        
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(headers)

        found_count = 0
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 設定台北時區
            tz_tw = timezone(timedelta(hours=8))
            now_tw = datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')
            
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    
                    # 修正 API 欄位對應邏輯
                    # AvailableReturnBikes 是「可以歸還進來的車」，也就是現場「可借」的車
                    total_borrow = s.get('AvailableReturnBikes', 0)
                    # AvailableRentSpaces 是「可以租借出去的空間」，也就是現場「空位」
                    empty_spaces = s.get('AvailableRentSpaces', 0)
                    
                    # 取得車種明細
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    # 邏輯補正：確保 一般+電輔 = 總數
                    if reg == 0 and ebike == 0 and total_borrow > 0:
                        reg = total_borrow
                    
                    writer.writerow([now_tw, name, total_borrow, reg, ebike, empty_spaces, uid])
                    print(f"✅ 數據入庫：{name} (可借:{total_borrow}, 空位:{empty_spaces})")
                    found_count += 1
        
        print(f"🏁 任務完成！本次成功紀錄 {found_count} 筆數據。")

except Exception as e:
    print(f"⚠️ 發生未知錯誤: {e}")
