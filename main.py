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
    # 步驟 A：先從「基本資訊」抓取所有站名與 ID 的對照表
    print("正在抓取站名與 ID 對照表...")
    station_url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Station/City/Kaohsiung?%24format=JSON"
    req_s = urllib.request.Request(station_url)
    req_s.add_header('Authorization', f'Bearer {token}')
    
    id_map = {}
    with urllib.request.urlopen(req_s) as res:
        station_data = json.loads(res.read().decode())
        for s in station_data:
            uid = s.get('StationUID')
            name = s.get('StationName', {}).get('Zh_tw', '')
            id_map[uid] = name

    # 步驟 B：抓取「即時動態」並與對照表合併
    print("正在對齊即時動態...")
    avail_url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
    req_a = urllib.request.Request(avail_url)
    req_a.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req_a) as res:
        avail_data = json.loads(res.read().decode())
        
        with open('all_ids_debug.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['UID', '站名', '可借'])
            
            for a in avail_data:
                uid = a.get('StationUID')
                name = id_map.get(uid, "未知站名")
                writer.writerow([uid, name, a.get('AvailableReturnBikes')])
                
                # 如果在對照表裡找到了楠梓高中，就印在日誌裡給我們看
                if "楠梓高中" in name:
                    print(f"🚩 抓到目標！站名: {name}, 它的 UID 是: {uid}")

    print("✅ 偵探任務完成！請查看 all_ids_debug.csv")

except Exception as e:
    print(f"⚠️ 錯誤: {e}")
