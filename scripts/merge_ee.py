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
    "广州综合", "广州新闻", "广州南国都市", "广东体育", "TVBJ1", "TVB1",
    "TVB星河", "广东珠江", "重温经典", "咪咕",
    # 新增移除项
    "海峡卫视", "五星体育", "iQIYI", "天映经典", "黄金华剧台"
]

# HK频道排序（按此顺序优先输出）
HK_TARGET_ORDER = [
    "凤凰中文", "凤凰资讯", "凤凰香港", "NOW新闻", "翡翠台", "翡翠一台", "TVB翡翠", "TVB翡翠(马来)", "TVB翡翠剧集台",
    "TVBJADE", "娱乐新闻", "无线新闻", "天映频道", "千禧经典", "明珠台", "八度空间",
    "TVB星河", "TVBPLUS", "TVBJ1", "TVB娱乐新闻", "TVB黄金华剧", "TVB功夫台", "TVB1",
    "HOY资讯", "HOYTV", "HOY77", "RTHK31", "RTHK32", "ROCK_Action", "MYTV黄金翡翠",
    "iQIYI", "Astro AEC", "Astro AOD", "Channel 5", "Channel 8", "Channel U",
    "ViuTVsix"
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
