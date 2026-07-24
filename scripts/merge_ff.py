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
# 已移除凤凰直连源，凤凰频道改从 SOURCE_URL 提取

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

BAD_KEYWORDS = ["测试", "购物", "广告"]

# 需要过滤删除的频道名称关键词/完整名称
FILTER_CHANNELS = [
    "雷霆881",
    "叱咤903",
    "AM864",
    "無線衛星亞洲台",
    "創世電視",
    "無線衛星新聞台",
    "亞洲新聞台",
    "半島电视台英語頻道",
    "France 24",
    "DW",
    "NHK World-Japan",
    "NewsWorld",
    "myTV SUPER 直播足球2台",
    "myTV SUPER 直播足球3台",
    "myTV SUPER 直播足球4台",
    "myTV SUPER 直播足球5台",
    "myTV SUPER 直播足球6台",
    "myTV SUPER 直播足球7台",
    "互动窗 1",
    "互动窗 2",
    "SUPER Kids Channel",
    "CCTV1港澳版",
    "澳视澳门",
    "澳视卫星",
    "澳门体育",
    "澳门综艺",
    "澳门莲花",
    "回看"
]

# ===================== 下载 =====================

def download(url, retry=2):
    headers = {"User-Agent": "Mozilla/5.0"}
    for i in range(retry):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            print(f"重试 {i+1} 失败: {url}, 错误: {str(e)[:50]}")
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
            name = name.strip()
            if not any(x in name for x in BAD_KEYWORDS):
                ext = f'#EXTINF:-1 group-title="未知",{name}'
                data.append((name, ext, url.strip()))
    return data

# 已移除 get_phoenix_channels 函数，凤凰频道改从主源提取

# 过滤指定不需要的频道
def filter_unwanted_channels(channel_list):
    result = []
    for name, ext, url in channel_list:
        skip_flag = False
        
        # 1. 匹配黑名单关键词（包含澳门系列、CCTV1港澳版、回看等）
        for bad_name in FILTER_CHANNELS:
            if bad_name in name:
                skip_flag = True
                break
                
        # 2. 正则精确过滤 CCTV1 到 CCTV17
        if not skip_flag:
            if re.search(r'CCTV[-_\s]?(1[0-7]|[1-9])(?!\d)', name, re.IGNORECASE):
                skip_flag = True
                
        if not skip_flag:
            result.append((name, ext, url))
    return result

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

# ===================== 主程序 =====================

def main():
    print("主源...")
    main_data = parse_m3u(download(SOURCE_URL))

    print("TW...")
    tw_data = parse_m3u(download(TW_M3U_URL))

    # -------------------------------------------
    # 修改：从主源提取凤凰频道，并分离出 HK 分组（不含凤凰）
    # -------------------------------------------
    phoenix_raw = []
    hk_raw = []
    for n, e, u in main_data:
        if "凤凰" in n or "鳳凰" in n:
            phoenix_raw.append((n, e, u))
        else:
            group = parse_group(e)
            if group in HK_GROUPS:
                hk_raw.append((n, e, u))

    phoenix_raw = dedup(phoenix_raw)
    hk_raw = dedup(hk_raw)

    # 将指定的三个核心凤凰频道挑出来放最前面
    phoenix_top = []
    phoenix_other = []
    top_keywords = ["凤凰中文", "凤凰资讯", "凤凰香港", "鳳凰中文", "鳳凰資訊", "鳳凰香港"]
    for n, e, u in phoenix_raw:
        if any(tk in n for tk in top_keywords):
            phoenix_top.append((n, e, u))
        else:
            phoenix_other.append((n, e, u))

    # 直连源重组：指定的核心凤凰排在最最前面
    phoenix_ordered = phoenix_top + phoenix_other

    # 合并：核心凤凰置顶 -> 其他凤凰 -> 主源HK常规频道
    all_hk_raw = phoenix_ordered + hk_raw
    # -------------------------------------------

    # 统一过滤黑名单频道 (包含CCTV1-17、澳门系列以及所有带“回看”的频道)
    all_hk_clean = filter_unwanted_channels(all_hk_raw)

    # 截断优化：剔除 Action Hollywood Movies 频道后面的所有频道
    truncated_hk = []
    for n, e, u in all_hk_clean:
        truncated_hk.append((n, e, u))
        if "Action Hollywood Movies" in n:
            print(f"📌 已捕获截断点频道: {n}，其后的所有频道已被剔除。")
            break
    all_hk_clean = truncated_hk

    # 去重TW并同样过滤一遍不需要的频道
    tw = filter_unwanted_channels(dedup(tw_data))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    out = "#EXTM3U\n\n"
    out += f"# 更新时间 {now}\n\n"

    # 读取BB.m3u并去除末尾多余空行
    try:
        with open(BB_FILE, encoding="utf-8") as f:
            bb_lines = f.readlines()
            for l in bb_lines:
                if not l.startswith("#EXTM3U"):
                    out += l
            out = out.rstrip('\n')
            out += '\n'
    except FileNotFoundError:
        print("未找到 BB.m3u，跳过加载")
    except Exception as e:
        print("读取BB.m3u出错:", str(e))

    # HK分组
    out += "# HK\n"
    for n, e, u in all_hk_clean:
        new_ext = set_group(e, "HK")
        out += new_ext + "\n" + u + "\n"

    # TW分组
    out += "\n# TW\n"
    for n, e, u in tw:
        new_ext = set_group(e, "TW")
        out += new_ext + "\n" + u + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(out)

    print("✅ 完成，已生成", OUTPUT_FILE)

if __name__ == "__main__":
    main()
