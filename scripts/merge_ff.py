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
HK_M3U_URL = "http://45.32.81.163:30000/mytv.m3u?token=juli"  # 新的HK订阅源

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

# HK分组只提取mytv
HK_GROUP = "mytv"

BAD_KEYWORDS = ["测试", "购物", "广告"]

# 凤凰系列关键词（用于排序）
PHOENIX_KEYWORDS = ["凤凰中文", "凤凰资讯", "凤凰香港"]
PHOENIX_ORDER = {name: idx for idx, name in enumerate(PHOENIX_KEYWORDS)}

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

def is_cctv(name):
    """判断是否为CCTV1~CCTV17"""
    # 匹配 CCTV1 到 CCTV17（包括 CCTV-1 到 CCTV-17 格式）
    pattern = r'^CCTV[-\s]?([1-9]|1[0-7])($|\s|:)'
    return bool(re.search(pattern, name, re.IGNORECASE))

def sort_hk_channels(channels):
    """对HK频道排序：凤凰系列排最前面"""
    phoenix = []
    others = []
    
    for item in channels:
        name = item[0]
        # 检查是否为凤凰系列（精确匹配）
        is_phoenix = False
        for kw in PHOENIX_KEYWORDS:
            if kw in name:
                phoenix.append(item)
                is_phoenix = True
                break
        if not is_phoenix:
            others.append(item)
    
    # 对凤凰系列按指定顺序排序
    phoenix.sort(key=lambda x: PHOENIX_ORDER.get(
        next((kw for kw in PHOENIX_KEYWORDS if kw in x[0]), ""), 999
    ))
    
    return phoenix + others

# ===================== 主程序 =====================

def main():
    print("主源...")
    main_data = parse_m3u(download(SOURCE_URL))

    print("TW...")
    tw_data = parse_m3u(download(TW_M3U_URL))
    
    print("HK (mytv)...")
    hk_raw = parse_m3u(download(HK_M3U_URL))

    # 从HK源中提取group-title="mytv"的分组
    hk = []
    for n, e, u in hk_raw:
        group = parse_group(e)
        if group == HK_GROUP:
            # 过滤CCTV1~CCTV17
            if not is_cctv(n):
                hk.append((n, e, u))
    
    # 去重
    hk = dedup(hk)
    tw = dedup(tw_data)
    
    # 对HK频道排序（凤凰系列排最前面）
    hk = sort_hk_channels(hk)

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

    # HK分组（凤凰系列已排最前面）
    out += "# HK\n"
    for n, e, u in hk:
        out += (set_group(e, "HK") or "") + "\n" + (u or "") + "\n"

    # TW分组
    out += "\n# TW\n"
    for n, e, u in tw:
        out += (set_group(e, "TW") or "") + "\n" + (u or "") + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"✅ 完成！HK频道数: {len(hk)}, TW频道数: {len(tw)}")

if __name__ == "__main__":
    main()
