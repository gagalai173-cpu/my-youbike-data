import urllib.request
import json
import csv
import os
from datetime import datetime

# TDX 訪客連結
url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
target_name = "楠梓高中"
file_name = 'youbike_log.csv'

# 準備檔案標題
if not os.path.exists(file_name):
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['時間', '站名', '可借車輛', '可還空位'])

try:
    # 使用內建的 urllib 代替 requests
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode())
        
        found = False
        for s in data:
            name = s.get('StationName', {}).get('Zh_tw', '')
            if target_name in name:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                row = [now, name, s.get('AvailableReturnBikes'), s.get('AvailableRentSpaces')]
                
                with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                
                print(f"✅ 成功寫入: {name}")
                found = True
                break
        
        if not found:
            print(f"❌ 找不到站點: {target_name}")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
