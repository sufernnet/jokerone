#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== 路径 =====================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

SOURCE_URL = "https://yang.sufern001.workers.dev/"
OUTPUT_FILE = os.path.join(ROOT_DIR, "EE.m3u")
BB_FILE = os.path.join(ROOT_DIR, "BB.m3u")

HK_SOURCE_GROUP = "• Juli 「精選」"
TW_SOURCE_GROUP = "•台湾「限制」"

# ===================== ⭐ 港澳台精选（替换 HK） =====================

# HK新源
HK_NEW_SOURCE = "https://cdn.qd.je/live.m3u"
HK_GROUP_NAME = "HK"

# HK需要过滤掉的频道列表
HK_FILTER_LIST = [
    "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV5+", "CCTV6", "CCTV7", "CCTV8",
    "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17",
    "CCTV1港澳版", "澳视澳门", "澳视卫星", "澳门体育", "澳门综艺", "澳门莲花",
    "金光布袋戏", "民视影剧台", "公视戏剧", "采昌影剧台", "靖天映画", "靖天戏剧台",
    "靖天电影台", "靖洋戏剧台", "影迷数位电影台", "amc电影台", "CinemaWorld",
    "My Cinema Europe", "经典电影台", "CMusic", "DreamWorks梦工厂动画",
    "精选动漫台", "纬来电影台", "纬来戏剧台", "纬来体育台",
    "东森电影", "东森戏剧", "东森洋片", "咪咕4K(限移动网络)", "咪咕4K-2(限移动网络)"
]

# HK频道排序（按此顺序优先输出）
HK_TARGET_ORDER = [
    "凤凰中文", "凤凰资讯", "凤凰香港", "NOW新闻", "翡翠台", "翡翠一台", "TVB翡翠", "TVB翡翠(马来)", "TVB翡翠剧集台",
    "TVBJADE", "娱乐新闻", "无线新闻", "天映频道", "千禧经典", "明珠台", "八度空间",
    "TVB星河", "TVBPLUS", "TVBJ1", "TVB娱乐新闻", "TVB黄金华剧", "TVB功夫台", "TVB1",
    "HOY资讯", "HOYTV", "HOY77", "RTHK31", "RTHK32", "ROCK_Action", "MYTV黄金翡翠",
    "iQIYI", "Astro AEC", "Astro AOD", "Channel 5", "Channel 8", "Channel U"
]

# ===================== TW 新源 =====================

TW_NEW_SOURCE = "https://github.com/sufernnet/jokerone/blob/main/OFIII.m3u"
# 注意：如果上述源无法访问，代码会自动回退到原有的TW提取逻辑

# ===================== EXTRA =====================

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

CCTV_TARGET = [
    "世界地理", "兵器科技", "怀旧剧场", "第一剧场",
    "女性时尚", "风云足球", "风云音乐", "央视台球"
]

# 👉 MV（替代原CHC）
# 使用更灵活的关键词匹配，方便匹配不同的变体
MV_TARGET_ORDER = [
    ("CHC动作电影", ["CHC动作电影", "CHC动作电影台", "CHC动作", "动作电影", "CHC动作电影HD"]),
    ("CHC家庭影院", ["CHC家庭影院", "CHC家庭电影", "家庭影院", "CHC家庭影院HD"]),
    ("CHC影迷电影", ["CHC影迷电影", "CHC影迷", "影迷电影", "CHC影迷电影HD"]),
    ("ROCK Action", ["ROCK Action", "ROCK Action", "ROCK Action HD"]),
    ("ROCK Xstream", ["ROCK Xstream", "ROCK Xstream", "ROCK Xstream HD"]),
    ("ROCK Entertainment", ["ROCK Entertainment", "ROCK Entertainment", "ROCK Entertainment HD"]),
    ("HBO王牌", ["HBO王牌", "HBO", "HBO HD"]),
    ("Cinemax", ["Cinemax", "Cinemax HD"]),
    ("Cinemax精选", ["Cinemax精选", "Cinemax精选HD"]),
    ("龙华电影", ["龙华电影", "龙华电影HD"]),
    ("龙华经典", ["龙华经典", "龙华经典HD"]),
    ("龙华偶像", ["龙华偶像", "龙华偶像HD"]),
    ("龙华日韩", ["龙华日韩", "龙华日韩HD"]),
    ("北京IPTV淘电影", ["北京IPTV淘电影", "淘电影"]),
    ("北京IPTV4K", ["北京IPTV4K", "北京IPTV 4K"]),
    ("天映频道", ["天映频道", "天映"]),
    ("天映新加坡", ["天映新加坡", "天映新加坡频道"]),
    ("爱奇艺", ["爱奇艺", "iQIYI"]),
    ("TVB星河", ["TVB星河", "星河频道"]),
]

LONGHUA_KEYWORDS = ["龙华电影", "龙华经典", "龙华偶像", "龙华日韩"]

LOGO_MAP = {
    "CHC影迷电影": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CHC影迷电影.png",
    "CHC家庭影院": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CHC家庭影院.png",
    "CHC动作电影": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CHC动作电影.png"
}

# ===================== TW 排序 =====================

TW_TARGET_ORDER = [
    "Love Nature",
    "History 歷史頻道",
    "亞洲旅遊",
    "中天新聞台",
    "民視第一台",
    "民視台灣台",
    "民視",
    "華視",
    "寰宇新聞",
    "寰宇新聞台灣台",
    "寰宇財經",
    "三立綜合台",
    "ELTA娛樂",
    "靖天綜合",
    "鏡電視新聞台",
    "東森新聞",
    "華視新聞",
    "民視新聞",
    "三立iNEWS",
    "東森財經新聞",
    "中視新聞",
    "TVBS",
    "民視綜藝",
    "靖天育樂",
    "靖天國際台",
    "靖天歡樂台",
    "靖天資訊",
    "TVBS歡樂台",
    "韓國娛樂台",
    "ROCK Entertainment",
    "Lifetime 娛樂頻道",
    "電影原聲台CMusic",
    "TRACE Urban",
    "Mezzo Live HD",
    "INULTRA",
    "TRACE Sport Stars",
    "智林體育",
    "時尚運動X",
    "車迷 TV",
    "GINX Esports TV",
    "民視旅遊",
    "滾動力 Rollor",
    "TVBS新聞台",
    "un探索娛樂台",
    "ELTATW",
    "MagellanTV頻道",
    "民視影劇",
    "HITS頻道",
    "八大精彩",
    "FashionTV 時尚頻道",
    "CI 罪案偵查頻道",
    "視納華仁紀實頻道",
    "影迷數位紀實台",
    "采昌影劇",
    "靖天映畫",
    "靖天電影",
    "影迷數位電影台",
    "amc 電影台",
    "Cinema World",
    "My Cinema Europe HD 我的歐洲電影",
    "CNBC Asia 財經台",
    "經典電影台",
    "中視",
    "中視新聞",
    "華視新聞",
    "三立新聞iNEWS",
    "DayStar"
]

# ===================== 下载 =====================

def download(url, retry=3):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for i in range(retry):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            if i < retry - 1:
                time.sleep(2)
    return ""

# ===================== 工具 =====================

def clean_name(name):
    name = re.sub(r'[\(\[\{（【].*?[\)\]\}）】]', '', name)
    name = re.sub(r'「.*?」', '', name)
    return name.strip()

def parse_name(extinf):
    return clean_name(extinf.split(",", 1)[-1])

def parse_group(extinf):
    m = re.search(r'group-title="([^"]*)"', extinf)
    return m.group(1) if m else ""

def normalize_group(extinf, group):
    if not extinf:
        return f'#EXTINF:-1 group-title="{group}",未知'
    if 'group-title="' in extinf:
        result = re.sub(r'group-title="[^"]*"', f'group-title="{group}"', extinf)
    else:
        result = extinf.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"')
    return result if result else extinf

def dedup(data):
    seen = set()
    out = []
    for n, e, u in data:
        if u not in seen:
            seen.add(u)
            out.append((n, e, u))
    return out

# ===================== 解析 =====================

def parse_m3u(content):
    lines = content.splitlines()
    out = []
    ext = None
    for l in lines:
        l = l.strip()
        if l.startswith("#EXTINF"):
            ext = l
        elif l.startswith("http") and ext:
            name = parse_name(ext)
            out.append((name, ext, l))
            ext = None
    return out

# ===================== HK（新源） =====================

def load_hk():
    """从 https://cdn.qd.je/live.m3u 加载HK频道，并过滤掉指定列表"""
    raw = download(HK_NEW_SOURCE)
    if not raw:
        print("⚠️ 无法下载HK新源")
        return []
    
    data = parse_m3u(raw)
    print(f"✓ 从HK新源获取到 {len(data)} 个频道")
    
    # 过滤掉指定的频道
    filtered = []
    for n, e, u in data:
        # 检查是否在过滤列表中
        should_filter = False
        for filter_name in HK_FILTER_LIST:
            if filter_name in n:
                should_filter = True
                break
        if not should_filter:
            filtered.append((n, e, u))
    
    print(f"✓ 过滤后剩余 {len(filtered)} 个频道")
    
    # 按指定顺序排序
    result = []
    temp_dict = {}
    for n, e, u in filtered:
        # 如果同一个频道有多个URL，保留第一个
        if n not in temp_dict:
            temp_dict[n] = (n, e, u)
    
    used_names = set()
    for target in HK_TARGET_ORDER:
        matched = None
        for name in temp_dict.keys():
            if target in name or name in target:
                matched = name
                break
        if matched and matched not in used_names:
            result.append(temp_dict[matched])
            used_names.add(matched)
    
    # 添加未在排序列表中的其他频道（去重）
    for n in temp_dict.keys():
        if n not in used_names:
            result.append(temp_dict[n])
            used_names.add(n)
    
    return result

# ===================== TW（新源合并） =====================

def load_tw_from_new_source():
    """尝试从新源加载TW频道"""
    raw = download(TW_NEW_SOURCE)
    if not raw:
        print("⚠️ 无法下载TW新源，将使用原有逻辑")
        return None
    data = parse_m3u(raw)
    print(f"✓ 从TW新源获取到 {len(data)} 个频道")
    # 按指定顺序排序
    result = []
    temp_dict = {}
    for n, e, u in data:
        if n not in temp_dict:
            temp_dict[n] = (n, e, u)
    
    used_names = set()
    for target in TW_TARGET_ORDER:
        matched = None
        for name in temp_dict.keys():
            if target in name or name in target:
                matched = name
                break
        if matched and matched not in used_names:
            result.append(temp_dict[matched])
            used_names.add(matched)
    
    # 添加未在排序列表中的其他频道
    for n in temp_dict.keys():
        if n not in used_names:
            result.append(temp_dict[n])
            used_names.add(n)
    
    return result

def fetch_tw(lines):
    """原有TW提取逻辑（作为备选）"""
    parsed = parse_m3u("\n".join(lines))
    
    # 收集所有TW分组的频道
    temp_dict = {}  # key: 频道名, value: (name, ext, url)
    for n, e, u in parsed:
        if parse_group(e) == TW_SOURCE_GROUP:
            # 去掉「」及其内部内容
            cleaned_name = re.sub(r'「[^」]*」', '', n)
            cleaned_name = cleaned_name.strip()
            if not cleaned_name:
                cleaned_name = n
            
            # 清理extinf行中的名称
            ext_parts = e.split(",", 1)
            if len(ext_parts) == 2:
                cleaned_ext_name = re.sub(r'「[^」]*」', '', ext_parts[1])
                cleaned_ext_name = cleaned_ext_name.strip()
                if not cleaned_ext_name:
                    cleaned_ext_name = ext_parts[1]
                cleaned_ext = ext_parts[0] + "," + cleaned_ext_name
            else:
                cleaned_ext = e
            
            # 如果同一个频道有多个URL，保留第一个
            if cleaned_name not in temp_dict:
                temp_dict[cleaned_name] = (cleaned_name, cleaned_ext, u)
    
    # 按指定顺序排序
    result = []
    used_names = set()
    
    for target in TW_TARGET_ORDER:
        # 精确匹配或包含匹配
        matched = None
        for name in temp_dict.keys():
            if name == target or target in name or name in target:
                matched = name
                break
        
        if matched and matched not in used_names:
            result.append(temp_dict[matched])
            used_names.add(matched)
    
    return result

# ===================== MV =====================

def load_mv():
    print("开始加载MV频道...")
    
    # 主要源：用于提取原有MV频道以及新增的北京/港澳台频道
    main_source_url = "https://github.chenc.dev/raw.githubusercontent.com/CKL1211/eric/refs/heads/master/MyIPTV.m3u"
    raw_main = download(main_source_url)
    if not raw_main:
        print("⚠️ 无法下载主要MV源，尝试其他备选源...")
        all_data = []
        
        # 尝试其他备选源
        backup_sources = [
            "https://raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u",
            "https://live.kilvn.com/iptv.m3u",
        ]
        for src in backup_sources:
            raw = download(src)
            if raw:
                all_data.extend(parse_m3u(raw))
                print(f"✓ 从备选源获取到数据: {src}")
                break
    else:
        all_data = parse_m3u(raw_main)
        print(f"✓ 从主源获取到 {len(all_data)} 个频道")
    
    if not all_data:
        print("❌ 所有源都无法获取数据")
        return []
    
    # 统计各分组频道数量
    group_stats = {}
    for n, e, u in all_data:
        group = parse_group(e)
        group_stats[group] = group_stats.get(group, 0) + 1
    
    # 针对新增频道的精确提取：从"北京"分组提取北京IPTV淘电影、北京IPTV4K；从"港澳台"分组提取天映频道、天映新加坡、爱奇艺、TVB星河
    # 同时保留原有MV频道的提取逻辑（放宽分组限制）
    temp = []
    
    print("正在筛选符合条件的频道...")
    
    for n, e, u in all_data:
        group = parse_group(e)
        # 原有MV频道提取条件：分组包含综合/电影/影视/MV/娱乐，或频道名包含CHC/龙华/ROCK/HBO/Cinemax
        original_condition = (any(keyword in group for keyword in ["综合", "电影", "影视", "MV", "娱乐", "影視"]) or
                              any(keyword in n for keyword in ["CHC", "龙华", "ROCK", "HBO", "Cinemax", "动作电影", "家庭影院", "影迷电影"]))
        
        # 新增频道提取条件：精确匹配分组和频道名
        beijing_condition = (group == "北京" and 
                             any(target in n for target in ["北京IPTV淘电影", "北京IPTV4K", "淘电影", "4K"]))
        hk_tw_condition = (group == "港澳台" and 
                           any(target in n for target in ["天映频道", "天映新加坡", "爱奇艺", "TVB星河", "天映", "iQIYI", "星河"]))
        
        if original_condition or beijing_condition or hk_tw_condition:
            # 打印找到的候选频道（调试用）
            if "CHC" in n or "动作" in n:
                print(f"  【候选】频道: {n}, 分组: {group}")
            temp.append((clean_name(n), e, u))
    
    temp = dedup(temp)
    print(f"筛选后剩余 {len(temp)} 个候选频道")
    
    result = []
    for target_name, keywords in MV_TARGET_ORDER:
        candidates = []
        for n, e, u in temp:
            # 检查是否匹配任一关键词
            for kw in keywords:
                if kw.lower() in n.lower():
                    candidates.append((n, e, u))
                    break
        
        if candidates:
            # 去重URL
            unique_candidates = []
            seen_urls = set()
            for n, e, u in candidates:
                if u not in seen_urls:
                    seen_urls.add(u)
                    unique_candidates.append((n, e, u))
            
            if len(unique_candidates) > 1:
                print(f"  {target_name}: 找到 {len(unique_candidates)} 个候选URL，正在测速选择最优...")
            
            # 测速选最优
            urls = [u for _, _, u in unique_candidates]
            best_url = pick_best(urls)
            for n, e, u in unique_candidates:
                if u == best_url:
                    ext = e
                    if n in LOGO_MAP:
                        ext = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{LOGO_MAP[n]}"', ext)
                    result.append((target_name, ext, u))
                    print(f"✓ 找到MV频道: {target_name}")
                    break
        else:
            print(f"✗ 未找到MV频道: {target_name}")
    
    # 龙华频道排序
    non_lh = [x for x in result if not any(k in x[0] for k in LONGHUA_KEYWORDS)]
    lh = [x for x in result if any(k in x[0] for k in LONGHUA_KEYWORDS)]
    
    print(f"MV频道加载完成，共 {len(result)} 个频道")
    return non_lh + lh

# ===================== 测速 =====================

def check(url):
    try:
        t0 = time.time()
        r = requests.get(url, timeout=5, stream=True)
        if r.status_code == 200:
            return url, time.time() - t0
    except:
        pass
    return url, 999


def pick_best(urls):
    if not urls:
        return None
    best = None
    best_t = 999
    with ThreadPoolExecutor(max_workers=5) as ex:
        for f in as_completed([ex.submit(check, u) for u in urls]):
            u, t = f.result()
            if t < best_t:
                best, best_t = u, t
    return best

# ===================== 主程序 =====================

def main():
    print("=" * 50)
    print("开始生成EE.m3u...")
    print("=" * 50)

    content = download(SOURCE_URL)
    if not content:
        print("❌ 无法下载源文件")
        return

    lines = content.splitlines()

    print("正在加载HK频道...")
    hk = load_hk()
    print(f"HK频道加载完成，共 {len(hk)} 个")
    
    print("正在加载TW频道...")
    # 优先尝试新源，失败则回退到原有逻辑
    tw = load_tw_from_new_source()
    if tw is None:
        tw = fetch_tw(lines)
        print(f"TW频道使用原有逻辑加载完成，共 {len(tw)} 个")
    else:
        print(f"TW频道从新源加载完成，共 {len(tw)} 个")
    
    print("正在加载MV频道...")
    mv = load_mv()

    # 添加 EPG 信息头
    out = '#EXTM3U x-tvg-url="https://epg.zsdc.eu.org/t.xml.gz"\n\n'

    try:
        with open(BB_FILE, encoding="utf-8") as f:
            for l in f:
                if not l.startswith("#EXTM3U"):
                    out += l
    except Exception as e:
        print(f"⚠️ 无法读取 BB.m3u: {e}")

    # 去掉多余的空行
    lines_out = out.splitlines()
    cleaned_lines = []
    prev_empty = False
    for line in lines_out:
        is_empty = line.strip() == ""
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(line)
        prev_empty = is_empty
    out = "\n".join(cleaned_lines)

    # 添加MV分组
    if mv:
        if out.rstrip().endswith("\n"):
            out += "# MV\n"
        else:
            out += "\n# MV\n"
        for n, e, u in mv:
            out += normalize_group(e, "MV") + "\n" + u + "\n"
        out = out.rstrip() + "\n"

    if hk:
        if out.rstrip().endswith("\n"):
            out += "# HK\n"
        else:
            out += "\n# HK\n"
        for n, e, u in hk:
            out += normalize_group(e, "HK") + "\n" + u + "\n"
        out = out.rstrip() + "\n"

    if tw:
        if out.rstrip().endswith("\n"):
            out += "# TW\n"
        else:
            out += "\n# TW\n"
        for n, e, u in tw:
            out += normalize_group(e, "TW") + "\n" + u + "\n"
        out = out.rstrip() + "\n"

    # 最终清理多余空行
    final_lines = out.splitlines()
    final_cleaned = []
    prev_empty = False
    for line in final_lines:
        is_empty = line.strip() == ""
        if is_empty and prev_empty:
            continue
        final_cleaned.append(line)
        prev_empty = is_empty
    out = "\n".join(final_cleaned)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(out)

    print("=" * 50)
    print("✅ 完成！")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"HK频道数: {len(hk)}")
    print(f"TW频道数: {len(tw)}")
    print(f"MV频道数: {len(mv)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
