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
    # 呼叫「基本資訊」API
    url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Station/City/Kaohsiung?%24format=JSON"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        
        print(f"{'站名':<30} | {'身分證 ID (StationUID)':<15}")
        print("-" * 50)
        
        for s in data:
            addr = s.get('StationAddress', {}).get('Zh_tw', '')
            if "楠梓區" in addr:
                name = s.get('StationName', {}).get('Zh_tw', '')
                uid = s.get('StationUID', '')
                print(f"{name:<30} | {uid:<15}")

except Exception as e:
    print(f"⚠️ 查詢發生錯誤: {e}")
