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

# ===================== TW 分组（从远程 URL 加载） =====================

# TW 数据源 URL
TW_SOURCE_URL = "https://raw.githubusercontent.com/sufernnet/jokerone/refs/heads/main/TW.m3u"

# TW 排序列表（与您原有的一致）
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
    """只去除圆括号、方括号、花括号等，保留中文书名号《》及「」"""
    name = re.sub(r'[\(\[\{（【].*?[\)\]\}）】]', '', name)
    # 不再移除「...」，避免误删非后缀内容
    return name.strip()

def clean_suffix(name):
    """去除频道名称末尾的「...」形式后缀（如「Relay」、「4gTV」）"""
    return re.sub(r'「[^」]*」$', '', name).strip()

def replace_name_in_extinf(extinf, new_name):
    """将 #EXTINF 行中的频道名称替换为 new_name"""
    # 格式: #EXTINF:... ,原名称
    parts = extinf.rsplit(',', 1)
    if len(parts) == 2:
        return parts[0] + ',' + new_name
    return extinf  # 保底

def parse_name(extinf):
    raw = extinf.split(",", 1)[-1]
    # 先去除括号，再去掉末尾后缀
    return clean_suffix(clean_name(raw))

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
    raw = download(HK_NEW_SOURCE)
    if not raw:
        print("⚠️ 无法下载HK新源")
        return []
    data = parse_m3u(raw)
    print(f"✓ 从HK新源获取到 {len(data)} 个频道")
    filtered = []
    for n, e, u in data:
        if not any(f in n for f in HK_FILTER_LIST):
            filtered.append((n, e, u))
    print(f"✓ 过滤后剩余 {len(filtered)} 个频道")
    # 排序
    temp_dict = {n: (n, e, u) for n, e, u in filtered}
    result = []
    used = set()
    for target in HK_TARGET_ORDER:
        for name in temp_dict.keys():
            if target in name or name in target:
                if name not in used:
                    result.append(temp_dict[name])
                    used.add(name)
                break
    for name in temp_dict.keys():
        if name not in used:
            result.append(temp_dict[name])
    return result

# ===================== TW（从远程 URL 加载） =====================

def load_tw_from_url():
    raw = download(TW_SOURCE_URL)
    if not raw:
        print("⚠️ 无法下载TW数据源")
        return []
    data = parse_m3u(raw)
    print(f"✓ 从TW数据源获取到 {len(data)} 个频道")
    # 去重
    seen_urls = set()
    unique_data = []
    for n, e, u in data:
        if u not in seen_urls:
            seen_urls.add(u)
            unique_data.append((n, e, u))
    # 排序
    temp_dict = {n: (n, e, u) for n, e, u in unique_data}
    result = []
    used = set()
    for target in TW_TARGET_ORDER:
        for name in temp_dict.keys():
            if name == target or target in name or name in target:
                if name not in used:
                    result.append(temp_dict[name])
                    used.add(name)
                break
    for name in temp_dict.keys():
        if name not in used:
            result.append(temp_dict[name])
    print(f"✓ TW频道排序完成，共 {len(result)} 个")
    return result

# ===================== MV =====================

def load_mv():
    print("开始加载MV频道...")
    main_source = "https://github.chenc.dev/raw.githubusercontent.com/CKL1211/eric/refs/heads/master/MyIPTV.m3u"
    raw_main = download(main_source)
    if not raw_main:
        print("⚠️ 无法下载主要MV源，尝试其他备选源...")
        all_data = []
        backup = [
            "https://raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u",
            "https://live.kilvn.com/iptv.m3u",
        ]
        for src in backup:
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
    temp = []
    for n, e, u in all_data:
        group = parse_group(e)
        cond1 = any(k in group for k in ["综合", "电影", "影视", "MV", "娱乐", "影視"]) or \
                any(k in n for k in ["CHC", "龙华", "ROCK", "HBO", "Cinemax", "动作电影", "家庭影院", "影迷电影"])
        cond2 = (group == "北京" and any(k in n for k in ["北京IPTV淘电影", "北京IPTV4K", "淘电影", "4K"]))
        cond3 = (group == "港澳台" and any(k in n for k in ["天映频道", "天映新加坡", "爱奇艺", "TVB星河", "天映", "iQIYI", "星河"]))
        if cond1 or cond2 or cond3:
            cleaned = clean_suffix(clean_name(n))
            temp.append((cleaned, e, u))  # 注意此处 e 未改，但MV输出时我们也不替换名称（可保持原样，或用户未提及）
    temp = dedup(temp)
    result = []
    for target_name, keywords in MV_TARGET_ORDER:
        candidates = []
        for n, e, u in temp:
            if any(kw.lower() in n.lower() for kw in keywords):
                candidates.append((n, e, u))
        if candidates:
            unique_candidates = []
            seen_urls = set()
            for n, e, u in candidates:
                if u not in seen_urls:
                    seen_urls.add(u)
                    unique_candidates.append((n, e, u))
            urls = [u for _, _, u in unique_candidates]
            best_url = pick_best(urls)
            for n, e, u in unique_candidates:
                if u == best_url:
                    ext = e
                    if n in LOGO_MAP:
                        ext = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{LOGO_MAP[n]}"', ext)
                    result.append((target_name, ext, u))
                    break
        else:
            print(f"✗ 未找到MV频道: {target_name}")
    non_lh = [x for x in result if not any(k in x[0] for k in LONGHUA_KEYWORDS)]
    lh = [x for x in result if any(k in x[0] for k in LONGHUA_KEYWORDS)]
    print(f"MV频道加载完成，共 {len(result)} 个")
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

# ===================== 新增：从 SOURCE_URL 提取 Discovery 和 Sports =====================

def load_discovery(data):
    discovery_channels = []
    # 修改：移除了 "HBO"，只保留 BBC Earth 和 Discovery
    groups_keywords = {
        "•綜合「Relay」": ["BBC Earth", "Discovery"],
        "•台灣「Relay」": ["Love Nature", "History 歷史頻道", "動物星球"]
    }
    for group_name, keywords in groups_keywords.items():
        for n, e, u in data:
            if parse_group(e) != group_name:
                continue
            for kw in keywords:
                if kw.lower() in n.lower():
                    cleaned = clean_suffix(clean_name(n))
                    new_extinf = replace_name_in_extinf(e, cleaned)
                    discovery_channels.append((cleaned, new_extinf, u))
                    break
    discovery_channels = dedup(discovery_channels)
    # 删除过滤三个HBO的代码（因为不再包含HBO）
    print(f"✓ Discovery 分组提取到 {len(discovery_channels)} 个频道（已去除后缀）")
    return discovery_channels

# ===================== 修改后的 load_sports 函数 =====================
def load_sports(data):
    sports_channels = []
    # 不再从 other.m3u 提取五星体育，只保留提取 Apple TV 4K Dolby Vision F1
    other_url = "http://82.156.243.185:54321/other.m3u"
    raw_other = download(other_url)
    if raw_other:
        other_data = parse_m3u(raw_other)
        print(f"✓ 从other.m3u获取到 {len(other_data)} 个频道")
        # 提取 Apple TV 4K Dolby Vision F1（放在五星体育后面，但此处只提取）
        for n, e, u in other_data:
            if "Apple TV 4K Dolby Vision F1" in n:
                cleaned = clean_suffix(clean_name(n))
                new_extinf = replace_name_in_extinf(e, cleaned)
                sports_channels.append((cleaned, new_extinf, u))
                break
    else:
        print("⚠️ 无法下载other.m3u，跳过提取F1")

    # 原有的特定规则（已移除“五星体育”）
    specific_rules = [
        ("•香港「Relay」", ["Now Sports 精選", "Now Sports 英超 2台"]),
        ("•台灣「Relay」", ["緯來體育"])
    ]
    for group_name, keywords in specific_rules:
        for n, e, u in data:
            if parse_group(e) != group_name:
                continue
            for kw in keywords:
                if kw.lower() in n.lower():
                    cleaned = clean_suffix(clean_name(n))
                    new_extinf = replace_name_in_extinf(e, cleaned)
                    sports_channels.append((cleaned, new_extinf, u))
                    break
    # 提取 •體育「Relay」 所有频道
    for n, e, u in data:
        if parse_group(e) == "•體育「Relay」":
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            sports_channels.append((cleaned, new_extinf, u))
    sports_channels = dedup(sports_channels)
    print(f"✓ Sports 分组提取到 {len(sports_channels)} 个频道（已去除后缀，不含五星体育）")
    return sports_channels

# ===================== 主程序 =====================

def main():
    print("=" * 50)
    print("开始生成EE.m3u...")
    print("=" * 50)

    content = download(SOURCE_URL)
    if not content:
        print("❌ 无法下载源文件")
        return

    all_data = parse_m3u(content)
    print(f"✓ 从源文件解析到 {len(all_data)} 个频道条目")

    print("正在加载HK频道...")
    hk = load_hk()
    print(f"HK频道加载完成，共 {len(hk)} 个")
    print("正在加载TW频道（从远程URL加载）...")
    tw = load_tw_from_url()
    print(f"TW频道加载完成，共 {len(tw)} 个")
    print("正在加载MV频道...")
    mv = load_mv()
    print("正在加载 Discovery 分组...")
    discovery = load_discovery(all_data)
    print("正在加载 Sports 分组...")
    sports = load_sports(all_data)

    # ========== 新增：从 all_data 提取 HBO 频道并放入 MV ==========
    print("正在提取 HBO 频道（从 Relay 分组）并加入 MV...")
    hbo_list = []
    hbo_groups = ["•綜合「Relay」", "•台灣「Relay」"]
    # 过滤掉这三个 HBO 频道（与原来一致）
    hbo_filter = ["HBO Hits", "HBO Family", "HBO Signature"]
    for n, e, u in all_data:
        group = parse_group(e)
        if group not in hbo_groups:
            continue
        if "hbo" in n.lower():
            # 检查是否在过滤列表中
            if any(f.lower() in n.lower() for f in hbo_filter):
                continue
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            hbo_list.append((cleaned, new_extinf, u))
    hbo_list = dedup(hbo_list)
    if hbo_list:
        print(f"✓ 提取到 {len(hbo_list)} 个 HBO 频道，追加到 MV 分组")
        mv.extend(hbo_list)
        # 对 mv 去重（按 URL）
        mv = dedup(mv)
    else:
        print("⚠️ 未提取到 HBO 频道")

    # ========== 新增：硬编码五星体育（替换原有提取） ==========
    # 构造硬编码五星体育条目
    wxty_extinf = '#EXTINF:-1 group-title="Sports" tvg-logo="https://cdn.jsdelivr.net/gh/sparkssssssssss/epg/logo/wxty.png",五星体育'
    wxty_url = "https://cdn.qd.je/163189/wxty"
    wxty_entry = ("五星体育", wxty_extinf, wxty_url)
    # 插入到 sports 列表开头
    sports.insert(0, wxty_entry)
    print("✓ 已添加硬编码五星体育到 Sports 分组")

    # ========== 新增：从 MV 主源提取额外频道 ==========
    mv_url = "https://github.chenc.dev/raw.githubusercontent.com/CKL1211/eric/refs/heads/master/MyIPTV.m3u"
    mv_raw = download(mv_url)
    mv_parsed = parse_m3u(mv_raw) if mv_raw else []

    # 辅助提取函数（按分组和名称关键字）
    def extract_by_group_and_name(m3u_data, group_name, name_keywords):
        results = []
        for n, e, u in m3u_data:
            if parse_group(e) == group_name:
                for kw in name_keywords:
                    if kw.lower() in n.lower():
                        cleaned = clean_suffix(clean_name(n))
                        new_extinf = replace_name_in_extinf(e, cleaned)
                        results.append((cleaned, new_extinf, u))
                        break
        return results

    # 1. 提取广东体育（从「廣東台」分组）
    guangdong_sports = extract_by_group_and_name(mv_parsed, "廣東台", ["广东体育"])
    guangdong_channel = guangdong_sports[0] if guangdong_sports else None

    # 2. 提取 4K 分组中的四个指定频道
    fourk_names = ["北京IPTV4K", "爱上4K", "广东4K超高清", "南国都市4K"]
    fourk_channels = []
    for name in fourk_names:
        chs = extract_by_group_and_name(mv_parsed, "4K台", [name])
        if chs:
            fourk_channels.append(chs[0])

    # 3. 提取 BesTV4K 电影（放入 MV）
    bestv_movie = extract_by_group_and_name(mv_parsed, "4K台", ["BesTV4K电影"])
    # 4. 提取 BesTV4K 记录（放入 Discovery）
    bestv_doc = extract_by_group_and_name(mv_parsed, "4K台", ["BesTV4K记录"])
    # 5. 提取求索记录（从「數字台」分组）
    qiusuo_doc = extract_by_group_and_name(mv_parsed, "數字台", ["求索记录"])

    # 6. 获取 CCTV4K（从 all_data 中提取）
    cctv4k = None
    for n, e, u in all_data:
        if "CCTV4K" in n:
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            cctv4k = (cleaned, new_extinf, u)
            break

    # 构建 4K 分组列表（顺序：CCTV4K + 四个指定频道）
    fourk_list = []
    if cctv4k:
        fourk_list.append(cctv4k)
    fourk_list.extend(fourk_channels)

    # 将 BesTV4K 电影追加到 MV 分组末尾
    if bestv_movie:
        mv.append(bestv_movie[0])

    # 将 BesTV4K 记录和求索记录追加到 Discovery 分组末尾
    if bestv_doc:
        discovery.append(bestv_doc[0])
    if qiusuo_doc:
        discovery.append(qiusuo_doc[0])

    # 将广东体育插入 Sports 分组中“五星体育”之后
    if guangdong_channel:
        # 查找五星体育的索引（现在硬编码在开头）
        index = -1
        for i, (n, e, u) in enumerate(sports):
            if "五星体育" in n:
                index = i
                break
        if index != -1:
            sports.insert(index + 1, guangdong_channel)
        else:
            # 若未找到，则追加到末尾
            sports.append(guangdong_channel)

    # ========== 继续原有输出构建 ==========

    # 开始构建输出
    out = '#EXTM3U x-tvg-url="https://epg.zsdc.eu.org/t.xml.gz"\n\n'

    try:
        with open(BB_FILE, encoding="utf-8") as f:
            for l in f:
                if not l.startswith("#EXTM3U"):
                    out += l
    except Exception as e:
        print(f"⚠️ 无法读取 BB.m3u: {e}")

    # 清理多余空行
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

    # 分组输出
    def append_group(group_name, data):
        nonlocal out
        if data:
            if out.rstrip().endswith("\n"):
                out += f"# {group_name}\n"
            else:
                out += f"\n# {group_name}\n"
            for n, e, u in data:
                out += normalize_group(e, group_name) + "\n" + u + "\n"
            out = out.rstrip() + "\n"

    append_group("MV", mv)
    append_group("HK", hk)
    append_group("TW", tw)
    append_group("Discovery", discovery)
    append_group("Sports", sports)
    # 新增 4K 分组
    append_group("4K", fourk_list)

    # 最终清理空行
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
    print(f"Discovery频道数: {len(discovery)}")
    print(f"Sports频道数: {len(sports)}")
    print(f"4K频道数: {len(fourk_list)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
