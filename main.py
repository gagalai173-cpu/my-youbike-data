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
    # 我們改用「高雄市即時動態」的標準路徑
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        # --- DEBUG 區：讓我們看看資料到底長什麼樣 ---
        print(f"📡 成功讀取資料，總共 {len(data)} 個站點。")
        if len(data) > 0:
            print("📝 前 3 筆原始資料範例：")
            for i in range(min(3, len(data))):
                print(f"站點 {i+1}: {data[i]}")
        # ------------------------------------------

        found_count = 0
        file_name = 'nanzih_bike_data.csv'
        
        # 初始化檔案
        if not os.path.exists(file_name):
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(['時間', '站名', '可借總數', '可還空位', '一般車', '電輔車'])

        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for s in data:
                # 嘗試抓取各種可能的站名欄位
                name = s.get('StationName', {}).get('Zh_tw', '') or s.get('sna', '') or s.get('StationUID', '')
                
                # 只要包含「楠梓高中」就抓取
                if "楠梓高中" in name:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    total = s.get('AvailableReturnBikes', 0)
                    spaces = s.get('AvailableRentSpaces', 0)
                    detail = s.get('AvailableReturnBikesDetail', {})
                    reg = detail.get('GeneralBikes', 0)
                    ebike = detail.get('ElectricBikes', 0)
                    
                    writer.writerow([now, name, total, spaces, reg, ebike])
                    print(f"✅ 成功寫入: {name}")
                    found_count += 1
        
        print(f"🏁 搜尋結束，共找到 {found_count} 個符合的站點。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
