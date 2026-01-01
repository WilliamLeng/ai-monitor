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

# 实时新闻源 (RSS )
NEWS_SOURCES = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
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
                {"role": "system", "content": "你是一个资深 AI 行业分析师。请将英文动态翻译成中文，并将其分为两类：'🔥 核心必读'或 '📢 行业动态'。请简要说明理由。"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析失败: {str(e)}"

def fetch_real_time_news():
    """从 RSS 源抓取真实的最新新闻"""
    all_news = []
    print("正在抓取实时新闻...")
    for url in NEWS_SOURCES:
        try:
            resp = requests.get(url, timeout=15)
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
            for item in items[:5]:
                title_match = re.search(r'<title>(.*?)</title>', item, re.S)
                if title_match:
                    title = title_match.group(1)
                    title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                    all_news.append({"s": "实时新闻", "c": title})
        except Exception as e:
            print(f"抓取 {url} 失败: {e}")
    
    # 如果实时抓取不到，使用保底数据
    if not all_news:
        all_news = [
            {"s": "行业热点", "c": "OpenAI and other AI labs are shifting focus to agentic workflows in 2025."},
            {"s": "行业热点", "c": "Nvidia continues to dominate the AI chip market with new Blackwell architecture."},
            {"s": "行业热点", "c": "The debate over AI safety and open-source models intensifies globally."}
        ]
    return all_news[:10]

def send_to_all_groups(title, text):
    """循环发送到所有群组"""
    for url in WEBHOOK_LIST:
        if "access_token" not in url: continue
        try:
            resp = requests.post(url, json={
                "msgtype": "markdown", 
                "markdown": {"title": title, "text": text}
            })
            print(f"钉钉返回: {resp.text}")
        except Exception as e:
            print(f"发送失败: {e}")

def main():
    news_list = fetch_real_time_news()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    print(f"准备推送 {len(news_list)} 条资讯...")
    
    # 分两批发送，每批 5 条
    for i in range(0, len(news_list), 5):
        batch = news_list[i:i+5]
        # 标题开头直接放关键词 AI，确保 100% 匹配
        report = f"AI 实时资讯简报 (第{i//5 + 1}部分)\n时间: {now_str}\n\n"
        for item in batch:
            analysis = get_ai_analysis(f"Source: {item['s']}\nContent: {item['c']}")
            report += f"### 📍 {item['s']}\n{analysis}\n\n---\n"
        
        send_to_all_groups(f"AI 简报 Part {i//5 + 1}", report)

if __name__ == "__main__":
    main()
