import os
import requests
import json
import datetime
from openai import OpenAI

# 钉钉配置
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=6957a32622c091fdcc9150ec5ac55972a228ff82ff8e4a46205789fb108b72bb"

# 使用 DeepSeek API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY" ), 
    base_url="https://api.deepseek.com"
 )

def get_ai_summary(content):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的科技翻译和分析师。请将以下英文科技动态翻译成中文，并简要说明其重要性。"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"翻译失败: {str(e)}"

def send_dingtalk(text):
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "AI 科技资讯快报",
            "text": text
        }
    }
    r = requests.post(DINGTALK_WEBHOOK, headers=headers, data=json.dumps(data))
    return r.status_code

def fetch_latest_news():
    return [
        {"source": "Sam Altman (X)", "content": "Reflecting on 2025: The year AI agents joined the workforce. 2026 will be about autonomous coordination at scale."},
        {"source": "Andrej Karpathy (X)", "content": "2025 Year in Review: LLMs are no longer just chatbots; they are the new operating system for software creation. 'Vibe coding' is now mainstream."},
        {"source": "Nvidia / Groq News", "content": "Nvidia reportedly pays $20 billion for a major stake in AI chip startup Groq to bolster its inference capabilities."},
        {"source": "TechCrunch", "content": "2025 was the year AI got a 'vibe check'—moving from trillion-dollar infrastructure promises to real-world agentic deployment."}
    ]

def main():
    raw_data = fetch_latest_news()
    report = f"## 🚀 AI 科技资讯快报 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    for item in raw_data:
        summary = get_ai_summary(f"Source: {item['source']}\nContent: {item['content']}")
        report += f"### 📍 {item['source']}\n{summary}\n\n---\n"
    send_dingtalk(report)

if __name__ == "__main__":
    main()
