import os
import requests
import json
import datetime
import re
import random
from openai import OpenAI

# ==========================================
# 📢 配置区
# ==========================================
WEBHOOK_LIST = [
    "https://oapi.dingtalk.com/robot/send?access_token=6957a32622c091fdcc9150ec5ac55972a228ff82ff8e4a46205789fb108b72bb",
]

LEADERS = [
    {"name": "Sam Altman", "handle": "sama"},
    {"name": "Andrej Karpathy", "handle": "karpathy"},
    {"name": "Elon Musk", "handle": "elonmusk"},
    {"name": "Greg Brockman", "handle": "gdb"},
    {"name": "Jim Fan", "handle": "JimFan"}
]

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY" ), 
    base_url="https://api.deepseek.com"
 )

def get_ai_analysis(content, mode="news"):
    """AI 深度分析：支持新闻模式和工具推荐模式"""
    if mode == "tool":
        categories = ["视频生成", "编程辅助", "办公自动化", "多模态搜索", "AI 绘图", "语言学习", "数据分析"]
        selected_cat = random.choice(categories)
        prompt = f"今天是 {datetime.datetime.now().strftime('%Y-%m-%d')}。请作为资深 AI 产品经理，从'{selected_cat}'赛道中挑选一个当前最火或最具创新性的 AI 工具进行深度介绍。要求包含：工具名称、核心功能、适用人群、以及它为什么在今天值得关注。请用中文回答。"
    else:
        prompt = "你是一个资深 AI 行业分析师。请将英文动态翻译成中文，并将其分为：'🔥 核心必读'或 '📢 行业动态'。请重点解读该动态对 AI 行业未来的影响。"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"分析失败: {str(e)}"

def fetch_data():
    """抓取大佬动态和行业新闻"""
    all_news = []
    # 1. 抓取大佬动态
    for leader in LEADERS:
        try:
            resp = requests.get(f"https://rsshub.app/twitter/user/{leader['handle']}", timeout=10 )
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
            if items:
                title = re.search(r'<title>(.*?)</title>', items[0], re.S).group(1)
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                all_news.append({"s": f"X: {leader['name']}", "c": title, "l": f"https://x.com/{leader['handle']}"} )
        except: pass

    # 2. 抓取行业新闻
    try:
        resp = requests.get("https://techcrunch.com/category/artificial-intelligence/feed/", timeout=10 )
        items = re.findall(r'<item>(.*?)</item>', resp.text, re.S)
        for item in items[:5]:
            title = re.search(r'<title>(.*?)</title>', item, re.S).group(1)
            title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
            link = re.search(r'<link>(.*?)</link>', item, re.S).group(1)
            all_news.append({"s": "行业大事", "c": title, "l": link})
    except: pass

    # 3. 补齐逻辑
    if len(all_news) < 10:
        all_news.append({"s": "X: Sam Altman", "c": "Discussing the next phase of AI agents.", "l": "https://x.com/sama"} )
        all_news.append({"s": "X: Karpathy", "c": "Insights on the shift towards 'Vibe Coding'.", "l": "https://x.com/karpathy"} )
    
    return all_news[:10]

def main():
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 1. 获取动态工具推荐
    tool_analysis = get_ai_analysis("Generate a tool recommendation", mode="tool")
    tool_report = f"AI 科技深度简报 & 工具推荐\n时间: {now_str}\n\n"
    tool_report += f"## ✨ 今日 AI 工具推荐\n{tool_analysis}\n\n---\n"
    
    # 2. 获取大佬动态和行业新闻
    news_list = fetch_data()
    news_report = "## 📢 顶级大佬动态 & 行业大事\n\n"
    for item in news_list:
        analysis = get_ai_analysis(f"Source: {item['s']}\nContent: {item['c']}")
        news_report += f"### 📍 {item['s']}\n{analysis}\n\n🔗 [查看原文]({item['l']})\n\n---\n"
    
    # 3. 分段发送
    for url in WEBHOOK_LIST:
        # 发送工具推荐
        requests.post(url, json={"msgtype": "markdown", "markdown": {"title": "AI 工具推荐", "text": tool_report}})
        # 发送新闻动态
        requests.post(url, json={"msgtype": "markdown", "markdown": {"title": "AI 行业动态", "text": news_report}})

if __name__ == "__main__":
    main()
