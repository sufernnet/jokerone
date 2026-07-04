#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== 配置 =====================

SOURCE_URL = "https://yang.sufern001.workers.dev/"
TW_M3U_URL = "https://raw.githubusercontent.com/sufernnet/joker/main/TW.m3u"
PHOENIX_URL = "http://45.32.81.163:30000/mytv.m3u?token=juli"

EXTRA_URLS = [
    "https://tzdr.com/iptv.txt",
    "https://live.kilvn.com/iptv.m3u",
    "https://cdn.jsdelivr.net/gh/Guovin/iptv-api@gd/output/result.m3u",
    "https://gh-proxy.com/raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u",
    "http://175.178.251.183:6689/live.m3u",
    "https://m3u.ibert.me/ycl_iptv.m3u",
    "https://codeberg.org/Jsnzkpg/Jsnzkpg/raw/Jsnzkpg/Jsnzkpg1.m3u",
    "https://2026.xymm.ccwu.cc",
    "https://github.chenc.dev/raw.githubusercontent.com/CKL1211/eric/refs/heads/master/MyIPTV.m3u",
    "https://iptv.catvod.com/list.php?token=e222e4d00c9d1945c3387a6c63b434577afbefd92f01f3fa39da76f154997133"
]

OUTPUT_FILE = "Gather.m3u"
BB_FILE = "BB.m3u"

# 只提取这两个分组
HK_GROUPS = ["•香港「Relay」", "•myTV「DASH」"]

# 凤凰频道名称
PHOENIX_CHANNELS = ["凤凰中文", "凤凰资讯", "凤凰香港"]

BAD_KEYWORDS = ["测试", "购物", "广告"]

# 需要过滤的频道列表（包含这些关键词的频道及其后面的所有频道将被移除）
FILTER_CHANNELS = [
    "雷霆881", "叱咤903", "AM864", "無線衛星亞洲台", "創世電視", 
    "無線衛星新聞台", "亞洲新聞台", "半島電視台英語頻道", "France 24", 
    "DW", "NHK World-Japan", "NewsWorld", "myTV SUPER 直播足球2台", 
    "直播足球3台", "直播足球4台", "直播足球5台", "直播足球6台", "直播足球7台",
    "互動窗 1", "互動窗 2", "SUPER Kids Channel"
]

# ===================== 下载 =====================

def download(url, retry=2):
    headers = {"User-Agent": "Mozilla/5.0"}
    for i in range(retry):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.text
        except:
            print(f"重试 {i+1} 失败: {url}")
    print(f"跳过: {url}")
    return ""

# ===================== 解析 =====================

def parse_name(extinf):
    return extinf.split(",", 1)[-1].strip()

def parse_group(extinf):
    m = re.search(r'group-title="([^"]*)"', extinf)
    return m.group(1) if m else ""

def parse_m3u(content):
    lines = content.splitlines()
    data, ext = [], None

    for l in lines:
        l = l.strip()
        if l.startswith("#EXTINF"):
            ext = l
        elif l.startswith("http") and ext:
            name = parse_name(ext)
            if not any(x in name for x in BAD_KEYWORDS):
                data.append((name, ext, l))
    return data

def parse_txt(content):
    data = []
    for l in content.splitlines():
        if "," in l and "http" in l:
            name, url = l.split(",", 1)
            if not any(x in name for x in BAD_KEYWORDS):
                ext = f'#EXTINF:-1 group-title="未知",{name.strip()}'
                data.append((name.strip(), ext, url.strip()))
    return data

def load_extra():
    all_data = []
    for url in EXTRA_URLS:
        print("抓取:", url)
        raw = download(url)
        if not raw:
            continue
        try:
            if "#EXTINF" in raw:
                all_data += parse_m3u(raw)
            else:
                all_data += parse_txt(raw)
        except:
            print("解析失败:", url)
    return all_data

# ===================== 工具 =====================

def dedup(data):
    seen, out = set(), []
    for n, e, u in data:
        if u not in seen:
            seen.add(u)
            out.append((n, e, u))
    return out

def set_group(extinf, group):
    if extinf is None:
        return ""
    if 'group-title="' in extinf:
        return re.sub(r'group-title="[^"]*"', f'group-title="{group}"', extinf)
    return extinf.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"')

# ===================== 过滤函数 =====================

def filter_channels(data):
    """过滤指定频道及其后面的所有频道"""
    filtered = []
    stop = False
    
    for n, e, u in data:
        if stop:
            continue
            
        # 检查是否匹配过滤列表中的任意频道
        should_filter = False
        for filter_name in FILTER_CHANNELS:
            if filter_name in n:
                should_filter = True
                print(f"过滤频道: {n} (匹配: {filter_name})")
                stop = True  # 找到匹配项后停止后续所有频道
                break
        
        if not should_filter:
            filtered.append((n, e, u))
    
    return filtered

# ===================== 主程序 =====================

def main():
    print("主源...")
    main_data = parse_m3u(download(SOURCE_URL))

    print("TW...")
    tw_data = parse_m3u(download(TW_M3U_URL))
    
    print("凤凰源...")
    phoenix_data = parse_m3u(download(PHOENIX_URL))

    # 从主源中提取指定的HK分组
    hk = []
    for n, e, u in main_data:
        group = parse_group(e)
        if group in HK_GROUPS:
            hk.append((n, e, u))
    
    # 从凤凰源中提取"直连测试"分组中的凤凰频道
    phoenix_channels = []
    for n, e, u in phoenix_data:
        group = parse_group(e)
        if group == "直连测试":
            for phoenix in PHOENIX_CHANNELS:
                if phoenix in n:
                    phoenix_channels.append((n, e, u))
                    print(f"提取凤凰频道: {n}")
                    break
    
    # 将凤凰频道排在HK分组最前面（去重）
    phoenix_channels = dedup(phoenix_channels)
    
    # 从HK中移除可能重复的凤凰频道
    phoenix_names = set([n for n, _, _ in phoenix_channels])
    hk = [(n, e, u) for n, e, u in hk if n not in phoenix_names]
    
    # 合并：凤凰频道 + HK其他频道
    hk = phoenix_channels + hk
    hk = dedup(hk)
    
    # 去重TW
    tw = dedup(tw_data)
    
    # 应用过滤（移除指定频道及其后面的所有频道）
    tw = filter_channels(tw)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    out = "#EXTM3U\n\n"
    out += f"# 更新时间 {now}\n\n"

    # 读取BB.m3u并去除末尾多余空行
    try:
        with open(BB_FILE, encoding="utf-8") as f:
            bb_lines = f.readlines()
            for i, l in enumerate(bb_lines):
                if not l.startswith("#EXTM3U"):
                    out += l
            out = out.rstrip('\n')
            out += '\n'
    except:
        pass

    # HK分组（凤凰频道在最前面）
    out += "# HK\n"
    for n, e, u in hk:
        out += (set_group(e, "HK") or "") + "\n" + (u or "") + "\n"

    # TW分组（已过滤）
    out += "\n# TW\n"
    for n, e, u in tw:
        out += (set_group(e, "TW") or "") + "\n" + (u or "") + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(out)

    print("✅ 完成")
    print(f"HK频道数量: {len(hk)}")
    print(f"TW频道数量: {len(tw)}")

if __name__ == "__main__":
    main()
