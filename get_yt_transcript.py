from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from datetime import datetime
import json
import argparse
import os
import subprocess
from traceback import print_exc

def get_aim_json(aim):
    # 指定目标路径
    fname = f"ts_{aim}.json"
    os.makedirs("jsons", exist_ok=True)
    path = os.path.join("jsons", fname)
    # 不重复获取
    if os.path.exists(path):
        return path
    # 网络获取
    wpc = WebshareProxyConfig(proxy_username=args.proxy_username, proxy_password=args.proxy_password)
    ytt_api = YouTubeTranscriptApi(wpc)
    fetched_transcript = ytt_api.fetch(aim)

    raw_data = fetched_transcript.to_raw_data()

    # 存储数据
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)
    return path

def format_md(path):
    # 读取json
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 大锅烩算法
    text = " ".join([item["text"] for item in data if item["text"] not in ["[music]", ">> [music]"]])
    text = text.replace("[music]", "").replace(">> ", "\n\n🎙️ ")
    text = text.strip()
    
    return text

def merge_md(text, title, aim, tag, override=False):
    now = datetime.now()
    md = f"""---
title: {title}
description: Youtube {aim} 转写文稿
author: Github
pubDatetime: {now.isoformat()}
featured: false
draft: false
tags:
- Youtube
- 转写文稿
- {tag}
---

"""
    # 拼接内容
    content = md + text
    # 文件名
    fname = f"ytts_{aim}.md"
    os.makedirs("mds", exist_ok=True)
    path = os.path.join("mds", fname)
    if not override and os.path.exists(path):
        return path
    # 存储
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def playlist_agent(url, tag, lim=10):
    cp = subprocess.run(f'./yt-dlp.exe --flat-playlist -j "{url}" > {tag}.json.new', shell=True)
    if cp.returncode == 0:
        os.rename(f"{tag}.json.new", f"{tag}.json")
    else:
        os.remove(f"{tag}.json.new")
        return None
    # 获取目标
    with open(f"{tag}.json", "r", encoding="utf-8") as f:
        items = f.readlines()
        items = [i.strip() for i in items]

    res = []
    for item in items[-lim:]:
        aim_item = json.loads(item)
        
        aim = aim_item["id"]
        aim_title = aim_item["title"]
        
        json_path = get_aim_json(aim)
        text = format_md(json_path)
        
        md_path = merge_md(text, aim_title, aim, tag, override=False)
        res.append(md_path)
        print(f"{tag} - {aim}: {aim_title} is ok.")
    return res

def main(args):
    url = "https://www.youtube.com/playlist?list=PLpvZy2482-kjlxGoFLPHJFQ1lNRD_49uN"
    tag = "美国炼金术"
    try:
        res = playlist_agent(url, tag, lim=10)
    except:
        print_exc()
        
    print("ok")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--proxy_username", required=True, help="WebshareProxy")
    parser.add_argument("--proxy_password", required=True, help="WebshareProxy")
    
    args = parser.parse_args()
    
    main(args)