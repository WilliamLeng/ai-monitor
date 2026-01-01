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
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://www.wired.com/feed/category/ai/latest/rss"
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
        return f"分析失败: {str(e)}"

def fetch_real_time_news():
    """从 RSS 源抓取真实的最新新闻"""
    all_news = []
    print("正在抓取实时新闻...")
    for url in NEWS_SOURCES:
        try:
            # 使用简单的 requests 获取 RSS 内容（避免安装额外库）
            resp = requests.get(url, timeout=10)
            # 使用正则简单提取标题和链接（轻量化方案）
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
            for item in items[:5]: # 每个源取前 5 条
                title = re.search(r'<title>(.*?)</title>', item, re.S).group(1)
                # 去掉 CDATA 标签
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                all_news.append({"s": "行业新闻", "c": title})
        except Exception as e:
            print(f"抓取 {url} 失败: {e}")
    
    # 如果抓取失败，至少保留一些保底内容
    if not all_news:
        all_news = [{"s": "系统提示", "c": "今日暂无实时新闻更新，请检查网络连接。"}]
    
    return all_news[:10] # 最终取前 10 条

def send_to_all_groups(title, text):
    for url in WEBHOOK_LIST:
        if "access_token" not in url: continue
        requests.post(url, json={"msgtype": "markdown", "markdown": {"title": title, "text": text}})

def main():
    news_list = fetch_real_time_news()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 分两批发送
    for i in range(0, len(news_list), 5):
        batch = news_list[i:i+5]
        report = f"# 🤖 AI 实时资讯简报 (第{i//5 + 1}部分)\n> 时间: {now_str}\n\n"
        for item in batch:
            analysis = get_ai_analysis(f"Source: {item['s']}\nContent: {item['c']}")
            report += f"### 📍 {item['s']}\n{analysis}\n\n---\n"
        
        send_to_all_groups(f"AI 实时简报 Part {i//5 + 1}", report)

if __name__ == "__main__":
    main()
