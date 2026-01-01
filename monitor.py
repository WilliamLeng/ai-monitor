import requests
import json

# 确认 Webhook 地址
url = "https://oapi.dingtalk.com/robot/send?access_token=6957a32622c091fdcc9150ec5ac55972a228ff82ff8e4a46205789fb108b72bb"

def main( ):
    # 极简内容，开头强制带上关键词 AI
    payload = {
        "msgtype": "text",
        "text": {
            "content": "AI 科技资讯测试：如果你看到这条消息，说明通道是通的！"
        }
    }
    
    print("正在发送测试消息...")
    resp = requests.post(url, json=payload)
    print(f"钉钉服务器返回内容: {resp.text}")

if __name__ == "__main__":
    main()
