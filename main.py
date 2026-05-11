import requests
import pandas as pd
from datetime import datetime
import os

# 高雄 API 網址
url = "https://api.kcg.gov.tw/api/service/get/b4dd9c40-9027-4125-8666-06bef1756092"
target_name = "楠梓高中"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    stations = data.get('data', [])
    
    # 尋找目標站點
    for s in stations:
        if target_name in s.get('sna', ''):
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_data = {
                '時間': [now],
                '站名': [s.get('sna')],
                '可借車輛': [s.get('sbi')],
                '可還空位': [s.get('bemp')]
            }
            df_new = pd.DataFrame(new_data)
            
            # 如果檔案不存在就建立，存在就增加一行
            file_exists = os.path.isfile('youbike_log.csv')
            df_new.to_csv('youbike_log.csv', mode='a', index=False, header=not file_exists, encoding='utf-8-sig')
            print(f"成功記錄: {now}")
            break
except Exception as e:
    print(f"發生錯誤: {e}")
