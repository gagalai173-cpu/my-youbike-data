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
    # 使用「即時動態」API，這才包含電輔車數量
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        file_name = 'nanzih_bike_data.csv'
        # 準備老師指定的欄位
        headers = ['站名', '資料更新時間', '總可借車數', '可歸還車數', '一般車數量', '電輔車數量']
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            count = 0
            for s in data:
                name = s.get('StationName', {}).get('Zh_tw', '')
                
                # 同時監測您指定的兩站，或任何包含「楠梓」的站點
                if "楠梓" in name:
                    # 擷取 TDX 規格書定義的精確欄位
                    update_time = s.get('UpdateTime', '')
                    total_bikes = s.get('AvailableReturnBikes', 0)    # 總可借
                    return_spaces = s.get('AvailableRentSpaces', 0)   # 可歸還
                    regular_bikes = s.get('AvailableReturnBikesDetail', {}).get('GeneralBikes', 0) # 一般車
                    ebikes = s.get('AvailableReturnBikesDetail', {}).get('ElectricBikes', 0)       # 電輔車
                    
                    writer.writerow([name, update_time, total_bikes, return_spaces, regular_bikes, ebikes])
                    count += 1
            
            print(f"✅ 成功！已紀錄楠梓區共 {count} 個站點的詳細即時資訊。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
