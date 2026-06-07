from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import json
import argparse
import os

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


def main(args):
    # 获取目标
    with open("yt_plist.txt", "r", encoding="utf-8") as f:
        ids = f.readlines()
        ids = [i.strip() for i in ids]

    aim = ids[1]
    
    get_aim_json(aim)
        
    print("ok")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--proxy_username", required=True, help="WebshareProxy")
    parser.add_argument("--proxy_password", required=True, help="WebshareProxy")
    
    args = parser.parse_args()
    
    main(args)