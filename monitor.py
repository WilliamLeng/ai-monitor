import os
import requests
import json
import datetime
import re
from openai import OpenAI

# 1. 确认 Webhook 地址
WEBHOOK_LIST = [
    "https://oapi.dingtalk.com/robot/send?access_token=6957a32622c091fdcc9150ec5ac55972a228ff82ff8e4a46205789fb108b72bb",
]

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
        return f"分析失败: {str(e)}"

def main():
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 2. 核心内容：开头必须带有关键词 AI
    report_text = f"AI 科技资讯推送\n时间: {now_str}\n\n"
    
    # 模拟 3 条最核心的动态，确保内容不超长
    news_items = [
        {"s": "Sam Altman", "c": "AGI is becoming a technical reality faster than we anticipated."},
        {"s": "Andrej Karpathy", "c": "The future of programming is natural language interaction with LLMs."},
        {"s": "Nvidia", "c": "New Blackwell chips starting mass shipment to major data centers."}
    ]
    
    for item in news_items:
        analysis = get_ai_analysis(f"Source: {item['s']}\nContent: {item['c']}")
        report_text += f"【{item['s']}】\n{analysis}\n\n"
    
    # 3. 使用纯文本格式 (text) 而不是 markdown，这样最稳
    for url in WEBHOOK_LIST:
        payload = {
            "msgtype": "text",
            "text": {
                "content": report_text
            }
        }
        resp = requests.post(url, json=payload)
        print(f"发送结果: {resp.text}")

if __name__ == "__main__":
    main()
