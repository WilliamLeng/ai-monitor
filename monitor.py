import os
import requests
import json
import datetime
from openai import OpenAI

# 1. 请务必确认这个 Webhook 地址与你钉钉机器人里的一模一样
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=6957a32622c091fdcc9150ec5ac55972a228ff82ff8e4a46205789fb108b72bb"

# 使用 DeepSeek API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY" ), 
    base_url="https://api.deepseek.com"
 )

def get_ai_analysis(content):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个资深 AI 行业分析师。请将英文动态翻译成中文，并简要说明重要性。"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析失败: {str(e)}"

def main():
    # 2. 这里的标题包含了“AI”关键词，请确保你钉钉机器人的关键词设置里有“AI”
    report = f"# AI 科技深度简报测试\n> 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 先拿一条数据做测试
    test_content = "Sam Altman says AGI is coming soon."
    analysis = get_ai_analysis(test_content)
    report += f"### 📍 测试动态\n{analysis}\n\n"
    
    print("正在尝试发送到钉钉...")
    
    # 发送请求
    response = requests.post(DINGTALK_WEBHOOK, json={
        "msgtype": "markdown",
        "markdown": {"title": "AI 简报测试", "text": report}
    })
    
    # 3. 打印诊断信息
    print(f"发送状态码: {response.status_code}")
    print(f"钉钉服务器返回: {response.text}")
    
    if response.status_code != 200 or "errcode" in response.text and json.loads(response.text)["errcode"] != 0:
        print("❌ 发送失败，请检查上方返回的错误信息！")
    else:
        print("✅ 发送成功！请检查钉钉群。")

if __name__ == "__main__":
    main()
