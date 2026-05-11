import requests
import pandas as pd
from datetime import datetime
import os

# 高雄 API 網址 (確認是最新版)
url = "https://api.kcg.gov.tw/api/service/get/b4dd9c40-9027-4125-8666-06bef1756092"
target_name = "楠梓高中"

# 建立空檔案的保險，防止最後存檔報錯
if not os.path.isfile('youbike_log.csv'):
    pd.DataFrame(columns=['時間', '站名', '可借車輛', '可還空位']).to_csv('youbike_log.csv', index=False, encoding='utf-8-sig')

try:
    # 模擬瀏覽器訪問
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=15)
    data = response.json()
    stations = data.get('data', [])
    
    found = False
    for s in stations:
        # 使用更寬鬆的搜尋：只要名字有「楠梓高中」
        if target_name in s.get('sna', ''):
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_data = {
                '時間': [now],
                '站名': [s.get('sna')],
                '可借車輛': [s.get('sbi')],
                '可還空位': [s.get('bemp')]
            }
            df_new = pd.DataFrame(new_data)
            df_new.to_csv('youbike_log.csv', mode='a', index=False, header=False, encoding='utf-8-sig')
            print(f"✅ 成功抓取: {s.get('sna')} at {now}")
            found = True
            break
            
    if not found:
        print(f"❌ 在 {len(stations)} 個站點中找不到 '{target_name}'")
        # 即使找不到，我們也紀錄一筆「找不到」的紀錄，確保檔案有更新
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pd.DataFrame([{'時間': now, '站名': '找不到站點', '可借車輛': 0, '可還空位': 0}]).to_csv('youbike_log.csv', mode='a', index=False, header=False, encoding='utf-8-sig')

except Exception as e:
    print(f"⚠️ 發生錯誤: {e}")
