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
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Station/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        with open('nanzi_stations.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['站名', '位置描述', '緯度', '經度'])
            
            count = 0
            for s in data:
                # 取得站名與地址
                name = s.get('StationName', {}).get('Zh_tw', '')
                addr = s.get('StationAddress', {}).get('Zh_tw', '')
                
                # 只要站名或地址裡有「楠梓」，就記錄下來
                if "楠梓" in name or "楠梓" in addr:
                    lat = s.get('StationPosition', {}).get('PositionLat')
                    lon = s.get('StationPosition', {}).get('PositionLon')
                    
                    writer.writerow([name, addr, lat, lon])
                    count += 1
            
            print(f"✅ 修正成功！總共抓到 {count} 個位於楠梓的站點。")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
