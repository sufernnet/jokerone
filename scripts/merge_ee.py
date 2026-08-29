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

# HK需要过滤掉的频道列表（新增移除项）
HK_FILTER_LIST = [
    "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV5+", "CCTV6", "CCTV7", "CCTV8",
    "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17",
    "CCTV1港澳版", "澳视澳门", "澳视卫星", "澳门体育", "澳门综艺", "澳门莲花",
    "金光布袋戏", "民视影剧台", "公视戏剧", "采昌影剧台", "靖天映画", "靖天戏剧台",
    "靖天电影台", "靖洋戏剧台", "影迷数位电影台", "amc电影台", "CinemaWorld",
    "My Cinema Europe", "经典电影台", "CMusic", "DreamWorks梦工厂动画",
    "精选动漫台", "纬来电影台", "纬来戏剧台", "纬来体育台",
    "东森电影", "东森戏剧", "东森洋片", "咪咕4K(限移动网络)", "咪咕4K-2(限移动网络)",
    # 新增移除频道
    "广州综合", "广州新闻", "广州南国都市", "广东体育", "TVBJ1", "TVB1",
    "TVB星河", "广东珠江", "重温经典", "咪咕"
]

# HK频道排序（按此顺序优先输出）
HK_TARGET_ORDER = [
    "凤凰中文", "凤凰资讯", "凤凰香港", "NOW新闻", "翡翠台", "翡翠一台", "TVB翡翠", "TVB翡翠(马来)", "TVB翡翠剧集台",
    "TVBJADE", "娱乐新闻", "无线新闻", "天映频道", "千禧经典", "明珠台", "八度空间",
    "TVB星河", "TVBPLUS", "TVBJ1", "TVB娱乐新闻", "TVB黄金华剧", "TVB功夫台", "TVB1",
    "HOY资讯", "HOYTV", "HOY77", "RTHK31", "RTHK32", "ROCK_Action", "MYTV黄金翡翠",
    "iQIYI", "Astro AEC", "Astro AOD", "Channel 5", "Channel 8", "Channel U",
    "ViuTVsix"  # 新增
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

# 用于MV分组中CHC/HBO顺序控制的分类
CHC_KEYWORDS = ["CHC动作电影", "CHC家庭影院", "CHC影迷电影"]
HBO_KEYWORDS = ["HBO王牌", "Cinemax", "Cinemax精选"]
LONGHUA_KEYWORDS = ["龙华电影", "龙华经典", "龙华偶像", "龙华日韩", "龙华戏剧", "龙华洋片", "龙华卡通"]

LOGO_MAP = {
    "CHC影迷电影": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CHC影迷电影.png",
    "CHC家庭影院": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CHC家庭影院.png",
    "CHC动作电影": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CHC动作电影.png"
}

# ===================== 龙华系列新 Logo（用户提供） =====================
LONGHUA_LOGO_MAP = {
    "龙华电影": "https://iptv.yang-1989.xyz/logo/龍華電影台.webp",
    "龙华经典": "https://iptv.yang-1989.xyz/logo/龍華經典台.webp",
    "龙华偶像": "https://iptv.yang-1989.xyz/logo/龍華偶像台.webp",
    "龙华日韩": "https://iptv.yang-1989.xyz/logo/龍華日韓台.webp",
    "龙华戏剧": "https://iptv.yang-1989.xyz/logo/龍華戲劇台.webp",
    "龙华洋片": "https://iptv.yang-1989.xyz/logo/龍華洋片台.webp",
    "龙华卡通": "https://iptv.yang-1989.xyz/logo/龍華卡通台.webp",
}

# ===================== HK 频道图标映射（原有 + 覆盖） =====================
HK_LOGO_MAP = {
    "凤凰中文": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/凤凰中文.png",
    "凤凰资讯": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/凤凰资讯.png",
    "凤凰香港": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/凤凰香港.png",
    "NOW新闻": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/NOW新闻.png",
    "翡翠台": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/翡翠.png",
    "娱乐新闻": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/娱乐新闻.png",
    "无线新闻": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/无线新闻.png",
    "天映频道": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/天映.png",
    "千禧经典": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/千禧经典.png",
    "明珠台": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/明珠.png",
    "八度空间": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/八度空间.png",
    "HOY资讯": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/HOY78.png",
    "RTHK31": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/RTH31.png",
    "RTHK32": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/RTH32.png",
    "Astro AEC": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/Astro_AEC.png",
    "Astro AOD": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/Astro_AOD.png",
    "TVB Plus": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/TVBPLUS.png",
    "HOY TV": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/HOY77.png",
    "HOY国际财经台": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/HOY76.png",
    "ViuTV": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/VIUTV.png",
    "CH8": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/CH8.png",
    "CHU": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/Channel U.png",
    "ViuTVsix": "https://raw.githubusercontent.com/xiasufern/AA/main/icon/ViuTVsix.png",
}

# 用户提供的新 HK logo 覆盖（优先使用）
HK_LOGO_OVERRIDE = {
    "RTHK31": "https://iptv.yang-1989.xyz/logo/RTHK31.webp",
    "RTHK32": "https://iptv.yang-1989.xyz/logo/RTHK32.webp",
    "RTHK33": "https://iptv.yang-1989.xyz/logo/RTHK33.webp",
    "Channel 5": "https://iptv.yang-1989.xyz/logo/Channel%205.webp",
    "Channel 8": "https://iptv.yang-1989.xyz/logo/Channel%208.webp",
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
    return name.strip()

def clean_suffix(name):
    """去除频道名称末尾的「...」形式后缀（如「Relay」、「4gTV」）"""
    return re.sub(r'「[^」]*」$', '', name).strip()

def replace_name_in_extinf(extinf, new_name):
    """将 #EXTINF 行中的频道名称替换为 new_name"""
    parts = extinf.rsplit(',', 1)
    if len(parts) == 2:
        return parts[0] + ',' + new_name
    return extinf

def parse_name(extinf):
    raw = extinf.split(",", 1)[-1]
    return clean_suffix(clean_name(raw))

def parse_group(extinf):
    m = re.search(r'group-title="([^"]*)"', extinf)
    return m.group(1) if m else ""

def parse_tvg_logo(extinf):
    """从 #EXTINF 行中提取 tvg-logo"""
    m = re.search(r'tvg-logo="([^"]*)"', extinf)
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

def set_tvg_logo(extinf, logo_url):
    """在 extinf 中设置或替换 tvg-logo"""
    if not logo_url:
        return extinf
    if 'tvg-logo="' in extinf:
        return re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', extinf)
    else:
        if 'group-title="' in extinf:
            return extinf.replace('group-title="', f'tvg-logo="{logo_url}" group-title="', 1)
        else:
            return extinf.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo_url}"')

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
    """
    加载HK频道，返回 (hk_channels, longhua_channels)
    hk_channels: 过滤并排序后的HK频道（不含龙华及移除项）
    longhua_channels: 从HK源中提取的龙华系列频道
    """
    raw = download(HK_NEW_SOURCE)
    if not raw:
        print("⚠️ 无法下载HK新源")
        return [], []
    data = parse_m3u(raw)
    print(f"✓ 从HK新源获取到 {len(data)} 个频道")

    longhua_keywords = ["龙华电影", "龙华经典", "龙华偶像", "龙华日韩", "龙华戏剧", "龙华洋片", "龙华卡通"]
    remove_keywords = ["广州综合", "广州新闻", "广州南国都市", "广东体育", "TVBJ1", "TVB1",
                       "TVB星河", "广东珠江", "重温经典", "咪咕"]

    filtered = []
    longhua = []
    for n, e, u in data:
        if any(k in n for k in remove_keywords):
            continue
        if any(k in n for k in longhua_keywords):
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            longhua.append((cleaned, new_extinf, u))
            continue
        if any(f in n for f in HK_FILTER_LIST):
            continue
        cleaned = clean_suffix(clean_name(n))
        new_extinf = replace_name_in_extinf(e, cleaned)
        filtered.append((cleaned, new_extinf, u))

    print(f"✓ 过滤后剩余 {len(filtered)} 个频道，龙华提取 {len(longhua)} 个")

    # 为HK频道添加tvg-logo（原有映射）
    for i, (name, extinf, url) in enumerate(filtered):
        logo_url = None
        if name in HK_LOGO_MAP:
            logo_url = HK_LOGO_MAP[name]
        else:
            for key in HK_LOGO_MAP:
                if key in name or name in key:
                    logo_url = HK_LOGO_MAP[key]
                    break
        if logo_url:
            extinf = set_tvg_logo(extinf, logo_url)
            filtered[i] = (name, extinf, url)

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

    longhua.sort(key=lambda x: x[0])
    return result, longhua

# ===================== TW（从远程 URL 加载） =====================

def load_tw_from_url():
    raw = download(TW_SOURCE_URL)
    if not raw:
        print("⚠️ 无法下载TW数据源")
        return []
    data = parse_m3u(raw)
    print(f"✓ 从TW数据源获取到 {len(data)} 个频道")
    seen_urls = set()
    unique_data = []
    for n, e, u in data:
        if u not in seen_urls:
            seen_urls.add(u)
            unique_data.append((n, e, u))
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
            temp.append((cleaned, e, u))
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
                        ext = set_tvg_logo(ext, LOGO_MAP[n])
                    result.append((target_name, ext, u))
                    break
        else:
            print(f"✗ 未找到MV频道: {target_name}")

    # 按 CHC -> HBO/其他 -> 龙华 的顺序排列（龙华将在后续添加新logo后重新排序）
    chc_list = [x for x in result if any(k in x[0] for k in CHC_KEYWORDS)]
    hbo_list = [x for x in result if any(k in x[0] for k in HBO_KEYWORDS)]
    other_list = [x for x in result if not any(k in x[0] for k in CHC_KEYWORDS + HBO_KEYWORDS + LONGHUA_KEYWORDS)]
    longhua_list = [x for x in result if any(k in x[0] for k in LONGHUA_KEYWORDS)]

    result = chc_list + hbo_list + other_list + longhua_list
    print(f"MV频道加载完成，共 {len(result)} 个")
    return result

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

# ===================== Discovery（不含HBO） =====================

def load_discovery(data):
    discovery_channels = []
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
    print(f"✓ Discovery 分组提取到 {len(discovery_channels)} 个频道（已去除后缀）")
    return discovery_channels

# ===================== Sports（不含五星体育提取，使用硬编码） =====================

def load_sports(data):
    sports_channels = []
    # 只提取 Apple TV 4K Dolby Vision F1（不再提取五星体育）
    other_url = "http://82.156.243.185:54321/other.m3u"
    raw_other = download(other_url)
    if raw_other:
        other_data = parse_m3u(raw_other)
        print(f"✓ 从other.m3u获取到 {len(other_data)} 个频道")
        for n, e, u in other_data:
            if "Apple TV 4K Dolby Vision F1" in n:
                cleaned = clean_suffix(clean_name(n))
                new_extinf = replace_name_in_extinf(e, cleaned)
                sports_channels.append((cleaned, new_extinf, u))
                break
    else:
        print("⚠️ 无法下载other.m3u，跳过提取F1")

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
    for n, e, u in data:
        if parse_group(e) == "•體育「Relay」":
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            sports_channels.append((cleaned, new_extinf, u))
    sports_channels = dedup(sports_channels)
    print(f"✓ Sports 分组提取到 {len(sports_channels)} 个频道（不含五星体育）")
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

    # ========== 新增：从 all_data 提取特定频道 ==========
    print("正在从 SOURCE_URL 提取特定频道...")

    # 构建名称到 (extinf, url, logo) 的映射，用于后续查找 logo
    name_to_info = {}
    for n, e, u in all_data:
        cleaned = clean_suffix(clean_name(n))
        logo = parse_tvg_logo(e)
        if cleaned not in name_to_info:
            name_to_info[cleaned] = (e, u, logo)

    # 提取 PopC → MV
    popc_channel = None
    for n, e, u in all_data:
        if parse_group(e) == "•香港「Relay」" and "PopC" in n:
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            # 尝试从 name_to_info 获取 logo
            if cleaned in name_to_info and name_to_info[cleaned][2]:
                logo = name_to_info[cleaned][2]
                if 'tvg-logo="' not in new_extinf:
                    new_extinf = set_tvg_logo(new_extinf, logo)
            popc_channel = (cleaned, new_extinf, u)
            break

    # 提取 ViuTVsix → HK（同时从过滤列表中移除）
    viutvsix_channel = None
    for n, e, u in all_data:
        if parse_group(e) == "•香港「Relay」" and "ViuTVsix" in n:
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            if cleaned in name_to_info and name_to_info[cleaned][2]:
                logo = name_to_info[cleaned][2]
                if 'tvg-logo="' not in new_extinf:
                    new_extinf = set_tvg_logo(new_extinf, logo)
            viutvsix_channel = (cleaned, new_extinf, u)
            break

    # 提取 Now Sports 英超 → Sports
    now_sports_channel = None
    for n, e, u in all_data:
        if parse_group(e) == "•香港「Relay」" and "Now Sports 英超" in n:
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            if cleaned in name_to_info and name_to_info[cleaned][2]:
                logo = name_to_info[cleaned][2]
                if 'tvg-logo="' not in new_extinf:
                    new_extinf = set_tvg_logo(new_extinf, logo)
            now_sports_channel = (cleaned, new_extinf, u)
            break

    # 提取 愛爾達體育 一、二、三、四 → Sports
    elta_channels = []
    elta_names = ["愛爾達體育 一", "愛爾達體育 二", "愛爾達體育 三", "愛爾達體育 四"]
    for target in elta_names:
        for n, e, u in all_data:
            if parse_group(e) == "•台灣「Relay」" and target in n:
                cleaned = clean_suffix(clean_name(n))
                new_extinf = replace_name_in_extinf(e, cleaned)
                if cleaned in name_to_info and name_to_info[cleaned][2]:
                    logo = name_to_info[cleaned][2]
                    if 'tvg-logo="' not in new_extinf:
                        new_extinf = set_tvg_logo(new_extinf, logo)
                elta_channels.append((cleaned, new_extinf, u))
                break

    print(f"✓ 提取到 PopC: {popc_channel is not None}")
    print(f"✓ 提取到 ViuTVsix: {viutvsix_channel is not None}")
    print(f"✓ 提取到 Now Sports 英超: {now_sports_channel is not None}")
    print(f"✓ 提取到 愛爾達體育 共 {len(elta_channels)} 个")

    # ========== 继续加载其他分组 ==========
    print("正在加载HK频道...")
    hk, longhua = load_hk()
    # 将 ViuTVsix 加入 HK
    if viutvsix_channel:
        hk.append(viutvsix_channel)
        hk = dedup(hk)
        # 重新排序
        temp_dict = {n: (n, e, u) for n, e, u in hk}
        hk_sorted = []
        used = set()
        for target in HK_TARGET_ORDER:
            for name in temp_dict.keys():
                if target in name or name in target:
                    if name not in used:
                        hk_sorted.append(temp_dict[name])
                        used.add(name)
                    break
        for name in temp_dict.keys():
            if name not in used:
                hk_sorted.append(temp_dict[name])
        hk = hk_sorted

    # 为 HK 应用新的覆盖 logo（RTHK31, RTHK32, RTHK33, Channel 5, Channel 8）
    for i, (name, extinf, url) in enumerate(hk):
        if name in HK_LOGO_OVERRIDE:
            extinf = set_tvg_logo(extinf, HK_LOGO_OVERRIDE[name])
            hk[i] = (name, extinf, url)
        else:
            # 也可能名称不完全匹配，如 "Channel 5" 可能显示为 "CH5"，尝试包含匹配
            for key in HK_LOGO_OVERRIDE:
                if key in name or name in key:
                    extinf = set_tvg_logo(extinf, HK_LOGO_OVERRIDE[key])
                    hk[i] = (name, extinf, url)
                    break

    print(f"HK频道加载完成，共 {len(hk)} 个，龙华系列 {len(longhua)} 个")

    print("正在加载TW频道（从远程URL加载）...")
    tw = load_tw_from_url()
    print(f"TW频道加载完成，共 {len(tw)} 个")

    print("正在加载MV频道...")
    mv = load_mv()
    # 将 PopC 加入 MV
    if popc_channel:
        mv.append(popc_channel)
        mv = dedup(mv)
        print(f"✓ PopC 已加入 MV 分组")

    # 为龙华系列添加新 logo 并追加到 MV
    for i, (name, extinf, url) in enumerate(longhua):
        # 查找匹配的 logo
        logo_url = None
        for key in LONGHUA_LOGO_MAP:
            if key in name or name in key:
                logo_url = LONGHUA_LOGO_MAP[key]
                break
        if logo_url:
            extinf = set_tvg_logo(extinf, logo_url)
            longhua[i] = (name, extinf, url)
    mv.extend(longhua)
    mv = dedup(mv)

    # 确保龙华系列在 MV 末尾（先分离非龙华，再附加龙华）
    non_longhua = [x for x in mv if not any(k in x[0] for k in LONGHUA_KEYWORDS)]
    longhua_only = [x for x in mv if any(k in x[0] for k in LONGHUA_KEYWORDS)]
    mv = non_longhua + longhua_only
    print(f"MV频道合并后共 {len(mv)} 个（龙华在末尾）")

    print("正在加载 Discovery 分组...")
    discovery = load_discovery(all_data)
    print("正在加载 Sports 分组...")
    sports = load_sports(all_data)

    # 将 Now Sports 英超 和 愛爾達體育 加入 Sports
    if now_sports_channel:
        sports.append(now_sports_channel)
        print(f"✓ Now Sports 英超 已加入 Sports 分组")
    for ch in elta_channels:
        sports.append(ch)
    sports = dedup(sports)
    print(f"✓ 愛爾達體育 共 {len(elta_channels)} 个已加入 Sports 分组")
    print(f"Sports 分组当前共 {len(sports)} 个频道")

    # 硬编码五星体育（放在最前）
    wxty_extinf = '#EXTINF:-1 group-title="Sports" tvg-logo="https://cdn.jsdelivr.net/gh/sparkssssssssss/epg/logo/wxty.png",五星体育'
    wxty_url = "https://cdn.qd.je/163189/wxty"
    wxty_entry = ("五星体育", wxty_extinf, wxty_url)
    sports.insert(0, wxty_entry)
    print("✓ 已添加硬编码五星体育到 Sports 分组")

    # ========== 从 MV 主源提取额外频道 ==========
    mv_url = "https://github.chenc.dev/raw.githubusercontent.com/CKL1211/eric/refs/heads/master/MyIPTV.m3u"
    mv_raw = download(mv_url)
    mv_parsed = parse_m3u(mv_raw) if mv_raw else []

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

    # 广东体育
    guangdong_sports = extract_by_group_and_name(mv_parsed, "廣東台", ["广东体育"])
    guangdong_channel = guangdong_sports[0] if guangdong_sports else None

    # 4K频道
    fourk_names = ["北京IPTV4K", "爱上4K", "广东4K超高清", "南国都市4K"]
    fourk_channels = []
    for name in fourk_names:
        chs = extract_by_group_and_name(mv_parsed, "4K台", [name])
        if chs:
            fourk_channels.append(chs[0])

    # BesTV4K 电影 → 插入 MV 的 HBO 区域
    bestv_movie = extract_by_group_and_name(mv_parsed, "4K台", ["BesTV4K电影"])
    bestv_doc = extract_by_group_and_name(mv_parsed, "4K台", ["BesTV4K记录"])
    qiusuo_doc = extract_by_group_and_name(mv_parsed, "數字台", ["求索记录"])

    # CCTV4K
    cctv4k = None
    for n, e, u in all_data:
        if "CCTV4K" in n:
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            cctv4k = (cleaned, new_extinf, u)
            break

    fourk_list = []
    if cctv4k:
        fourk_list.append(cctv4k)
    fourk_list.extend(fourk_channels)

    # BesTV4K 电影 → 插入 MV 的 HBO 区域后面
    if bestv_movie:
        hbo_indices = [i for i, (n, e, u) in enumerate(mv) if any(k in n for k in HBO_KEYWORDS)]
        if hbo_indices:
            insert_pos = max(hbo_indices) + 1
            mv.insert(insert_pos, bestv_movie[0])
        else:
            mv.append(bestv_movie[0])
        mv = dedup(mv)
        print(f"✓ BesTV4K电影 已插入 MV 分组的 HBO 区域后面")

    if bestv_doc:
        discovery.append(bestv_doc[0])
    if qiusuo_doc:
        discovery.append(qiusuo_doc[0])

    if guangdong_channel:
        index = -1
        for i, (n, e, u) in enumerate(sports):
            if "五星体育" in n:
                index = i
                break
        if index != -1:
            sports.insert(index + 1, guangdong_channel)
        else:
            sports.append(guangdong_channel)

    # ========== 提取HBO并加入MV（从 all_data 补充） ==========
    print("正在提取 HBO 频道（从 Relay 分组）并加入 MV...")
    hbo_list = []
    hbo_groups = ["•綜合「Relay」", "•台灣「Relay」"]
    hbo_filter = ["HBO Hits", "HBO Family", "HBO Signature"]
    for n, e, u in all_data:
        group = parse_group(e)
        if group not in hbo_groups:
            continue
        if "hbo" in n.lower():
            if any(f.lower() in n.lower() for f in hbo_filter):
                continue
            cleaned = clean_suffix(clean_name(n))
            new_extinf = replace_name_in_extinf(e, cleaned)
            if cleaned in name_to_info and name_to_info[cleaned][2]:
                logo = name_to_info[cleaned][2]
                if 'tvg-logo="' not in new_extinf:
                    new_extinf = set_tvg_logo(new_extinf, logo)
            hbo_list.append((cleaned, new_extinf, u))
    hbo_list = dedup(hbo_list)
    if hbo_list:
        print(f"✓ 提取到 {len(hbo_list)} 个 HBO 频道，追加到 MV 分组")
        hbo_indices = [i for i, (n, e, u) in enumerate(mv) if any(k in n for k in HBO_KEYWORDS)]
        if hbo_indices:
            insert_pos = max(hbo_indices) + 1
            for ch in reversed(hbo_list):
                mv.insert(insert_pos, ch)
        else:
            mv.extend(hbo_list)
        mv = dedup(mv)
    else:
        print("⚠️ 未提取到 HBO 频道")

    # 再次确保龙华在 MV 末尾（因为插入可能打乱）
    non_longhua = [x for x in mv if not any(k in x[0] for k in LONGHUA_KEYWORDS)]
    longhua_only = [x for x in mv if any(k in x[0] for k in LONGHUA_KEYWORDS)]
    mv = non_longhua + longhua_only

    # ========== 对 Sports 分组进行自定义排序 ==========
    def sports_sort_key(item):
        name = item[0]
        # 定义优先级顺序
        order = [
            "五星体育", "广东体育", "Apple TV", "Now Sports", "愛爾達體育",
            "緯來體育", "Eurosport"
        ]
        for idx, keyword in enumerate(order):
            if keyword.lower() in name.lower():
                return idx
        return len(order)  # 其他

    sports.sort(key=sports_sort_key)
    print("✓ Sports 分组已按指定顺序排序")

    # ========== 构建输出 ==========
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
