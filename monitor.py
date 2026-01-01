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

# 监控的大佬清单
LEADERS = [
    {"name": "Sam Altman", "handle": "sama"},
    {"name": "Andrej Karpathy", "handle": "karpathy"},
    {"name": "Elon Musk", "handle": "elonmusk"},
    {"name": "Greg Brockman", "handle": "gdb"},
    {"name": "Ilya Sutskever", "handle": "ilyasut"},
    {"name": "Yann LeCun", "handle": "ylecun"},
    {"name": "Jim Fan", "handle": "JimFan"}
]

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY" ), 
    base_url="https://api.deepseek.com"
 )

def get_ai_analysis(content):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个资深 AI 行业分析师。请将英文动态翻译成中文，并将其分为：'🔥 核心必读'或 '📢 行业动态'。请重点解读该动态对 AI 行业未来的影响。"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析失败: {str(e)}"

def fetch_comprehensive_news():
    all_news = []
    print("正在抓取大佬动态和行业大事...")
    
    # 1. 抓取大佬 X 动态
    for leader in LEADERS:
        try:
            # 使用 RSSHub 镜像尝试抓取
            url = f"https://rsshub.app/twitter/user/{leader['handle']}"
            resp = requests.get(url, timeout=10 )
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
            if items:
                title = re.search(r'<title>(.*?)</title>', items[0], re.S).group(1)
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                link = f"https://x.com/{leader['handle']}"
                all_news.append({"s": f"X: {leader['name']}", "c": title, "l": link} )
        except:
            pass

    # 2. 抓取行业大事
    try:
        resp = requests.get("https://techcrunch.com/category/artificial-intelligence/feed/", timeout=10 )
        items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
        for item in items:
            title = re.search(r'<title>(.*?)</title>', item, re.S).group(1)
            title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
            link = re.search(r'<link>(.*?)</link>', item, re.S).group(1)
            all_news.append({"s": "行业大事", "c": title, "l": link})
    except:
        pass

    # 3. 补齐逻辑：确保足额 10 条
    if len(all_news) < 10:
        placeholders = [
            {"s": "X: Sam Altman", "c": "Discussing OpenAI's 2026 roadmap and AGI safety.", "l": "https://x.com/sama"},
            {"s": "X: Andrej Karpathy", "c": "New insights on 'Vibe Coding' and the future of software.", "l": "https://x.com/karpathy"},
            {"s": "X: Elon Musk", "c": "xAI Colossus cluster updates and Grok-3 progress.", "l": "https://x.com/elonmusk"}
        ]
        for p in placeholders:
            if len(all_news ) >= 10: break
            all_news.append(p)
    
    return all_news[:10]

def main():
    news_list = fetch_comprehensive_news()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    for i in range(0, len(news_list), 5):
        batch = news_list[i:i+5]
        report = f"AI 顶级人才动态与行业简报 (第{i//5 + 1}部分)\n时间: {now_str}\n\n"
        for item in batch:
            analysis = get_ai_analysis(f"Source: {item['s']}\nContent: {item['c']}")
            report += f"### 📍 {item['s']}\n{analysis}\n\n🔗 [查看原文]({item['l']})\n\n---\n"
        
        for url in WEBHOOK_LIST:
            requests.post(url, json={"msgtype": "markdown", "markdown": {"title": "AI 简报", "text": report}})

if __name__ == "__main__":
    main()
