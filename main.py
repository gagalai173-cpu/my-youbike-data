import requests
import pandas as pd
from datetime import datetime
import os

# 改用 TDX 訪客模式的 API 連結 (高雄市即時車位資訊)
# TDX 平台對開發者較友善，通常不會阻擋 GitHub Actions
url = "https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/Kaohsiung?%24format=JSON"
target_name = "楠梓高中"

# 建立檔案保險
if not os.path.isfile('youbike_log.csv'):
    pd.DataFrame(columns=['時間', '站名', '可借車輛', '可還空位']).to_csv('youbike_log.csv', index=False, encoding='utf-8-sig')

try:
    # 訪客模式不需要金鑰，直接請求即可
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        stations = response.json()
        found = False
        
        for s in stations:
            # TDX 的資料結構不同：名稱在 StationName -> Zh_tw 裡面
            station_name = s.get('StationName', {}).get('Zh_tw', '')
            
            if target_name in station_name:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # TDX 欄位：AvailableReturnBikes (可借), AvailableRentSpaces (可還)
                new_data = {
                    '時間': [now],
                    '站名': [station_name],
                    '可借車輛': [s.get('AvailableReturnBikes')],
                    '可還空位': [s.get('AvailableRentSpaces')]
                }
                df_new = pd.DataFrame(new_data)
                df_new.to_csv('youbike_log.csv', mode='a', index=False, header=False, encoding='utf-8-sig')
                print(f"✅ TDX 抓取成功: {station_name}")
                found = True
                break
        
        if not found:
            print(f"❌ TDX 資料庫中目前找不到包含 '{target_name}' 的站點")
    else:
        print(f"⚠️ TDX 伺服器回應錯誤碼: {response.status_code}")

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
