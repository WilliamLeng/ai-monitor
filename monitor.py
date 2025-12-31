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
    """获取 10 条最新的顶级动态"""
    # 这里的动态在实际运行中可以扩展为 RSS 抓取逻辑
    return [
        {"s": "Sam Altman", "c": "Reflecting on 2025: The year AI agents joined the workforce. 2026 will be about autonomous coordination at scale."},
        {"s": "Andrej Karpathy", "c": "2025 Year in Review: LLMs are no longer just chatbots; they are the new operating system for software creation. 'Vibe coding' is now mainstream."},
        {"s": "Nvidia / Groq", "c": "Nvidia reportedly pays $20 billion for a major stake in AI chip startup Groq to bolster its inference capabilities."},
        {"s": "OpenAI", "c": "Sam Altman confirms OpenAI is delaying its next open-weight model launch to conduct additional safety tests."},
        {"s": "Google DeepMind", "c": "AlphaFold 3 now predicts interactions for all life's molecules, accelerating drug discovery."},
        {"s": "Meta AI", "c": "Llama 4 training is underway with 10x more compute than Llama 3, aiming for AGI-level reasoning."},
        {"s": "Anthropic", "c": "Claude 4 achieves breakthrough in long-context reasoning and tool use efficiency."},
        {"s": "Elon Musk", "c": "xAI's Colossus cluster is now the world's most powerful AI training system with 100k H100s."},
        {"s": "TechCrunch", "c": "2025 was the year AI got a 'vibe check'—moving from infrastructure promises to real-world agentic deployment."},
        {"s": "The Verge", "c": "Apple integrates deeper AI features into its 2026 OS roadmap, focusing on local privacy-first agents."}
    ]

def main():
    raw_data = fetch_10_news()
    # 标题包含“AI”关键词以触发钉钉机器人
    report = f"# 🤖 AI 科技深度简报 (10条精选)\n> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    for item in raw_data:
        source = item.get('s')
        content = item.get('c')
        analysis = get_ai_analysis(f"Source: {source}\nContent: {content}")
        report += f"### 📍 {source}\n{analysis}\n\n---\n"
    
    # 发送并检查结果
    response = requests.post(DINGTALK_WEBHOOK, json={
        "msgtype": "markdown",
        "markdown": {"title": "AI 深度简报", "text": report}
    })
    
    if response.status_code == 200:
        print("✅ 10条深度资讯已成功推送到钉钉！")
    else:
        print(f"❌ 推送失败: {response.text}")

if __name__ == "__main__":
    main()
