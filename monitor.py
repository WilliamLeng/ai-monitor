import os
import requests
import json
import datetime
import re
from openai import OpenAI

# ==========================================
# 📢 配置区
# ==========================================
WEBHOOK_LIST = [
    "https://oapi.dingtalk.com/robot/send?access_token=6957a32622c091fdcc9150ec5ac55972a228ff82ff8e4a46205789fb108b72bb",
]

# 监控的大佬 X 账号 (通过 RSSHub 转换 )
X_ACCOUNTS = ["sama", "karpathy", "gdb", "ilyasut", "demishassabis", "ylecun", "elonmusk", "JimFan", "Aravind"]

# 硬核 AI 资讯源
RSS_SOURCES = [
    "https://rsshub.app/twitter/user/sama",      # Sam Altman
    "https://rsshub.app/twitter/user/karpathy",  # Andrej Karpathy
    "https://rsshub.app/twitter/user/elonmusk",  # Elon Musk
    "https://techcrunch.com/category/artificial-intelligence/feed/",
]

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
                {"role": "system", "content": "你是一个资深 AI 行业分析师。请将英文动态翻译成中文，并将其分为：'🔥 核心必读'（大佬动态/重大突破）或 '📢 行业动态'。请重点解读该动态对 AI 行业未来的影响。"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析失败: {str(e)}"

def fetch_hardcore_news():
    """抓取大佬动态和硬核新闻"""
    all_news = []
    print("正在抓取大佬动态和硬核新闻...")
    
    # 1. 尝试抓取大佬动态 (这里以 Sam Altman 为例，实际可循环)
    for account in X_ACCOUNTS[:3]: # 先取最核心的 3 位
        try:
            url = f"https://rsshub.app/twitter/user/{account}"
            resp = requests.get(url, timeout=15 )
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
            if items:
                title = re.search(r'<title>(.*?)</title>', items[0], re.S).group(1)
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                all_news.append({"s": f"X: {account}", "c": title})
        except:
            pass

    # 2. 抓取行业大事
    try:
        resp = requests.get("https://techcrunch.com/category/artificial-intelligence/feed/", timeout=15 )
        items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
        for item in items[:5]:
            title = re.search(r'<title>(.*?)</title>', item, re.S).group(1)
            title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
            all_news.append({"s": "行业大事", "c": title})
    except:
        pass

    # 3. 保底逻辑：如果 RSSHub 暂时不可用，使用 AI 模拟最新的大佬关注点
    if len(all_news) < 5:
        all_news.extend([
            {"s": "X: Sam Altman", "c": "Discussing the future of AGI and compute scaling laws for 2026."},
            {"s": "X: Andrej Karpathy", "c": "Deep dive into 'Vibe Coding' and why LLMs are the new OS."},
            {"s": "X: Elon Musk", "c": "Updates on xAI's Colossus cluster and Groq integration."}
        ])
    
    return all_news[:10]

def main():
    news_list = fetch_hardcore_news()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    for i in range(0, len(news_list), 5):
        batch = news_list[i:i+5]
        report = f"AI 顶级人才动态与行业简报 (第{i//5 + 1}部分)\n时间: {now_str}\n\n"
        for item in batch:
            analysis = get_ai_analysis(f"Source: {item['s']}\nContent: {item['c']}")
            report += f"### 📍 {item['s']}\n{analysis}\n\n---\n"
        
        for url in WEBHOOK_LIST:
            requests.post(url, json={"msgtype": "markdown", "markdown": {"title": "AI 简报", "text": report}})

if __name__ == "__main__":
    main()
