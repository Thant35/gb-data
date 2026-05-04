import os
import requests
import json
import base64
from datetime import datetime

# 1. သတ်မှတ်ချက်များ
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
REPO_NAME = "Thant35/gb-data"
FILE_PATH = "admin.json"
API_URL = "https://api.thaistock2d.com/live" 

# 2. GitHub ကနေ လက်ရှိ admin.json ကို ဖတ်ခြင်း
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
repo_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"

response = requests.get(repo_url, headers=headers)
if response.status_code == 200:
    file_data = response.json()
    sha = file_data['sha']
    content = base64.b64decode(file_data['content']).decode('utf-8')
    json_data = json.loads(content)
else:
    print("Error fetching GitHub file:", response.text)
    exit()

# 3. 2D API ကနေ ဂဏန်းအသစ် သွားယူခြင်း
try:
    api_resp = requests.get(API_URL).json()
    live_twod = api_resp.get('twod', '--') 
    
    current_hour = datetime.utcnow().hour
    # မြန်မာစံတော်ချိန် 12:01 PM (UTC 05:31) အတွက်
    if current_hour < 8: 
        json_data['noti']['m_result'] = str(live_twod)
    # မြန်မာစံတော်ချိန် 4:30 PM (UTC 10:00) အတွက်
    else: 
        json_data['noti']['e_result'] = str(live_twod)
        
except Exception as e:
    print("API Error:", e)

# 4. GitHub ထဲကို Update ပြန်လုပ်ခြင်း
updated_content = json.dumps(json_data, indent=2, ensure_ascii=False)
encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

update_payload = {
    "message": "🤖 AI Agent: Auto Updated 2D Result",
    "content": encoded_content,
    "sha": sha
}

put_resp = requests.put(repo_url, headers=headers, json=update_payload)
if put_resp.status_code == 200:
    print("✅ Successfully updated admin.json!")
else:
    print("❌ Failed to update:", put_resp.text)
