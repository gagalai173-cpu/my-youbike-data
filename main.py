import urllib.request
import json
import csv
import os
from datetime import datetime, timedelta, timezone

# --- 請填入你的 TDX 金鑰 ---
client_id = "gagalai.173-a1d531fc-3ae2-4793"
client_secret = "322266eb-18f5-4586-9ae4-e423b6996b87"
# ------------------------------

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
    # 回歸高雄可用的 v2 網址
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        headers = ['紀錄時間(台北)', '站名', '可借總數', '一般車', '電輔車', '可停空位', '站點UID']
        
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(headers)

        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            tz = timezone(timedelta(hours=8))
            now_tw = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            
            for s in data:
                uid = s.get('StationUID')
                if uid in target_ids:
                    name = target_ids[uid]
                    
                    # 根據之前的實測對齊欄位：
                    # 高雄 v2 裡，RentSpaces 是可借總數，ReturnBikes 是空位
                    can_borrow_total = s.get('AvailableRentSpaces', 0)
                    can_stop_spaces = s.get('AvailableReturnBikes', 0)
                    
                    # 抓取明細
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    # --- 強力邏輯修正 ---
                    # 1. 如果明細加總不等於總數，且總數 > 0，則進行校正
                    if (reg + ebike) != can_borrow_total and can_borrow_total > 0:
                        # 優先相信總數，若明細不足，將差額補到一般車
                        reg = can_borrow_total - ebike
                        if reg < 0: # 防呆，避免出現負數
                            reg = can_borrow_total
                            ebike = 0
                    
                    writer.writerow([now_tw, name, can_borrow_total, reg, ebike, can_stop_spaces, uid])
                    print(f"✅ 修正錄入：{name} (借:{can_borrow_total}, 停:{can_stop_spaces})")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
