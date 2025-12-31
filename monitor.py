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

def get_ai_analysis(content):
    """让 AI 进行深度分析和分级"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个资深 AI 行业分析师。请将英文动态翻译成中文，并将其分为两类：'🔥 核心必读'（对行业有重大影响）或 '📢 行业动态'（一般性更新）。请简要说明理由。"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"分析失败: {str(e)}"

def fetch_10_news():
    """模拟获取 10 条最新的顶级动态"""
    return [
        {"s": "Sam Altman", "c": "AGI is becoming a technical reality faster than we anticipated."},
        {"s": "Andrej Karpathy", "c": "The future of programming is natural language interaction with LLMs."},
        {"s": "Nvidia", "c": "New Blackwell chips starting mass shipment to major data centers."},
        {"s": "OpenAI", "c": "Introducing new safety protocols for autonomous agent coordination."},
        {"s": "Google DeepMind", "c": "AlphaFold 3 now predicts interactions for all life's molecules."},
        {"s": "Meta AI", "c": "Llama 4 training is underway with 10x more compute than Llama 3."},
        {"s": "Anthropic", "c": "Claude 4 achieves breakthrough in long-context reasoning."},
        {"s": "Elon Musk", "c": "xAI's Colossus cluster is now the world's most powerful AI training system."},
        {"s": "TechCrunch", "content": "AI startup funding hits all-time high in Q4 2025."},
        {"s": "The Verge", "content": "Apple integrates deeper AI features into its 2026 OS roadmap."}
    ]

def main():
    raw_data = fetch_10_news()
    report = f"# 🤖 AI 科技深度简报\n> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    for item in raw_data:
        content = item.get('c') or item.get('content')
        source = item.get('s') or item.get('source')
        analysis = get_ai_analysis(f"Source: {source}\nContent: {content}")
        report += f"### 📍 {source}\n{analysis}\n\n---\n"
    
    requests.post(DINGTALK_WEBHOOK, json={
        "msgtype": "markdown",
        "markdown": {"title": "AI 深度简报", "text": report}
    })

if __name__ == "__main__":
    main()
