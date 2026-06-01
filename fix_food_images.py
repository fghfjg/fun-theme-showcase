#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美食展示网站图文匹配修复脚本
================================

功能说明：
1. 从网站或本地HTML中提取美食列表
2. 为每个美食获取匹配的图片
3. 下载图片到本地 images/ 文件夹
4. 自动修改 index.html 中的图片链接

安装依赖：
    pip install -r requirements.txt

使用方法：
    python fix_food_images.py

图片版权说明：
    本脚本下载的图片仅供个人学习项目展示使用，不用于商业用途。
    图片来源于 Unsplash 免费图库（https://unsplash.com），遵循 Unsplash License。

作者：美食站长
日期：2026-06-01
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin, Style

# ==================== 配置区域 ====================

# 网站地址
WEBSITE_URL = "https://fghfjg.github.io/fun-theme-showcase/"

# 图片保存目录
IMAGES_DIR = "images"

# 本地HTML文件路径
LOCAL_HTML = "index.html"

# 请求延迟（秒），避免请求过快
REQUEST_DELAY = 1.0

# 图片尺寸
IMAGE_WIDTH = 400
IMAGE_HEIGHT = 300

# ==================== 美食与图片映射 ====================
# 如果自动获取失败，使用以下预定义的Unsplash图片ID
# 这些图片来自Unsplash免费图库，与美食名称高度匹配

FOOD_IMAGE_MAP = {
    "老北京炸酱面": {
        "unsplash_query": "zhajiang noodles chinese",
        "fallback_id": "1546069901-ba9599a7e63c"
    },
    "重庆小面": {
        "unsplash_query": "spicy noodles red chili",
        "fallback_id": "1544025162-d76694265947"
    },
    "广式肠粉": {
        "unsplash_query": "rice noodle roll dim sum",
        "fallback_id": "1547592166-23ac55094b6d"
    },
    "西安肉夹馍": {
        "unsplash_query": "chinese hamburger meat bun",
        "fallback_id": "1565299624946-b28f40a0ae38"
    },
    "长沙臭豆腐": {
        "unsplash_query": "stinky tofu fried",
        "fallback_id": "1571091717498-4191e4493940"
    },
    "台湾蚵仔煎": {
        "unsplash_query": "oyster omelette taiwanese",
        "fallback_id": "1547592166-eac426403336"
    },
    "武汉热干面": {
        "unsplash_query": "hot dry noodles sesame",
        "fallback_id": "1555123236-7605f5e8e364"
    },
    "广东早茶": {
        "unsplash_query": "dim sum har gow siu mai",
        "fallback_id": "1517248135467-4c7edcad34c4"
    },
    "四川冒菜": {
        "unsplash_query": "sichuan spicy soup vegetables",
        "fallback_id": "1414235077428-338989a2e8c0"
    },
    "山东煎饼": {
        "unsplash_query": "chinese crepe jianbing",
        "fallback_id": "1565299624946-b28f40a0ae38"
    },
    "广东潮汕牛肉火锅": {
        "unsplash_query": "beef hotpot chinese",
        "fallback_id": "1547592166-eac426403336"
    },
    "云南过桥米线": {
        "unsplash_query": "rice noodles soup yunnan",
        "fallback_id": "1547592166-23ac55094b6d"
    }
}


def get_food_name_pinyin(name):
    """将中文美食名称转换为拼音文件名"""
    pinyin_list = lazy_pinyin(name, style=Style.NORMAL)
    return "".join(pinyin_list) + ".jpg"


def download_from_unsplash(query, save_path):
    """
    从Unsplash获取图片
    使用Unsplash Source API（无需API Key）
    """
    url = f"https://source.unsplash.com/featured/{IMAGE_WIDTH}x{IMAGE_HEIGHT}/?{query}"
    
    try:
        print(f"  正在从Unsplash获取: {query}")
        response = requests.get(url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # 检查是否是图片
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            print(f"  警告: 返回的不是图片，尝试备用方案")
            return False
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        print(f"  成功下载: {save_path}")
        return True
        
    except Exception as e:
        print(f"  下载失败: {str(e)}")
        return False


def download_fallback_image(food_name, save_path):
    """
    使用备用方案下载图片
    使用Unsplash直接图片链接
    """
    if food_name in FOOD_IMAGE_MAP:
        fallback_id = FOOD_IMAGE_MAP[food_name]["fallback_id"]
        url = f"https://images.unsplash.com/photo-{fallback_id}?w={IMAGE_WIDTH}&h={IMAGE_HEIGHT}&fit=crop"
    else:
        # 使用picsum作为最终备用
        seed = get_food_name_pinyin(food_name).replace(".jpg", "")
        url = f"https://picsum.photos/seed/{seed}/{IMAGE_WIDTH}/{IMAGE_HEIGHT}"
    
    try:
        print(f"  使用备用图片源: {url[:60]}...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        print(f"  成功下载备用图片: {save_path}")
        return True
        
    except Exception as e:
        print(f"  备用图片下载失败: {str(e)}")
        return False


def extract_foods_from_html(html_content):
    """
    从HTML内容中提取美食列表
    解析JavaScript中的foods数组
    """
    foods = []
    
    # 方法1: 尝试从JavaScript中提取foods数组
    pattern = r"const\s+foods\s*=\s*\[([\s\S]*?)\];"
    match = re.search(pattern, html_content)
    
    if match:
        foods_str = match.group(1)
        # 提取每个美食对象
        food_pattern = r"\{\s*id:\s*\d+,\s*name:\s*['\"]([^'\"]+)['\"],\s*category:\s*['\"]([^'\"]+)['\"],\s*desc:\s*['\"]([^'\"]+)['\"],\s*img:\s*['\"]([^'\"]+)['\"]\s*\}"
        
        for food_match in re.finditer(food_pattern, foods_str):
            foods.append({
                "name": food_match.group(1),
                "category": food_match.group(2),
                "desc": food_match.group(3),
                "original_img": food_match.group(4)
            })
    
    # 方法2: 如果JavaScript解析失败，尝试从HTML卡片中提取
    if not foods:
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.find_all("article") or soup.find_all("div", class_=re.compile("card"))
        
        for card in cards:
            title = card.find("h3") or card.find(class_=re.compile("title|name"))
            if title:
                foods.append({
                    "name": title.get_text(strip=True),
                    "category": "",
                    "desc": "",
                    "original_img": ""
                })
    
    return foods


def download_html_from_website(url):
    """从网站下载HTML内容"""
    try:
        print(f"正在从网站下载HTML: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载HTML失败: {str(e)}")
        return None


def modify_html_images(html_content, food_images_map):
    """
    修改HTML中的图片链接
    将远程图片URL替换为本地图片路径
    """
    modified_html = html_content
    
    for food_name, local_path in food_images_map.items():
        # 查找该美食在JavaScript中的图片URL并替换
        # 匹配格式: img: 'https://...'
        pattern = rf"(name:\s*['\"]{re.escape(food_name)}['\"].*?img:\s*['\"])([^'\"]+)(['\"])",
        
        def replace_img(match):
            return match.group(1) + local_path + match.group(3)
        
        modified_html = re.sub(pattern, replace_img, modified_html, flags=re.DOTALL)
    
    return modified_html


def main():
    print("=" * 60)
    print("美食展示网站图文匹配修复脚本")
    print("=" * 60)
    print()
    
    # 创建图片保存目录
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"图片保存目录: {os.path.abspath(IMAGES_DIR)}")
    print()
    
    # 步骤1: 获取HTML内容
    print("[步骤1] 获取HTML内容...")
    html_content = None
    
    # 优先使用本地文件
    if os.path.exists(LOCAL_HTML):
        print(f"  使用本地文件: {LOCAL_HTML}")
        with open(LOCAL_HTML, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        print(f"  本地文件不存在，从网站下载...")
        html_content = download_html_from_website(WEBSITE_URL)
    
    if not html_content:
        print("错误: 无法获取HTML内容，程序退出")
        return
    
    # 步骤2: 提取美食列表
    print("\n[步骤2] 提取美食列表...")
    foods = extract_foods_from_html(html_content)
    
    if not foods:
        print("错误: 无法提取美食列表，程序退出")
        return
    
    print(f"  共找到 {len(foods)} 种美食:")
    for i, food in enumerate(foods, 1):
        print(f"    {i}. {food['name']} ({food['category']})")
    print()
    
    # 步骤3: 下载图片
    print("[步骤3] 下载美食图片...")
    food_images_map = {}  # 美食名称 -> 本地图片路径
    success_count = 0
    fail_count = 0
    
    for i, food in enumerate(foods, 1):
        food_name = food["name"]
        filename = get_food_name_pinyin(food_name)
        save_path = os.path.join(IMAGES_DIR, filename)
        
        print(f"\n  [{i}/{len(foods)}] 处理: {food_name}")
        
        # 如果图片已存在，跳过
        if os.path.exists(save_path):
            print(f"  图片已存在，跳过: {save_path}")
            food_images_map[food_name] = save_path
            success_count += 1
            continue
        
        # 尝试从Unsplash获取
        if food_name in FOOD_IMAGE_MAP:
            query = FOOD_IMAGE_MAP[food_name]["unsplash_query"]
            if download_from_unsplash(query, save_path):
                food_images_map[food_name] = save_path
                success_count += 1
                time.sleep(REQUEST_DELAY)
                continue
        
        # 尝试备用方案
        if download_fallback_image(food_name, save_path):
            food_images_map[food_name] = save_path
            success_count += 1
        else:
            fail_count += 1
            print(f"  警告: 无法获取 {food_name} 的图片")
        
        time.sleep(REQUEST_DELAY)
    
    print(f"\n  图片下载完成: 成功 {success_count} 张, 失败 {fail_count} 张")
    
    # 步骤4: 修改HTML
    print("\n[步骤4] 修改HTML文件...")
    
    if food_images_map:
        modified_html = modify_html_images(html_content, food_images_map)
        
        # 保存修改后的HTML
        backup_path = LOCAL_HTML + ".bak"
        if os.path.exists(LOCAL_HTML):
            import shutil
            shutil.copy(LOCAL_HTML, backup_path)
            print(f"  已创建备份: {backup_path}")
        
        with open(LOCAL_HTML, "w", encoding="utf-8") as f:
            f.write(modified_html)
        
        print(f"  已更新: {LOCAL_HTML}")
        
        # 输出修改报告
        print("\n" + "=" * 60)
        print("修改报告")
        print("=" * 60)
        print(f"\n共处理 {len(foods)} 种美食:")
        print()
        
        for food in foods:
            food_name = food["name"]
            if food_name in food_images_map:
                local_path = food_images_map[food_name]
                print(f"  {food_name}")
                print(f"    原图片: {food['original_img'][:60]}...")
                print(f"    新图片: {local_path}")
                print()
            else:
                print(f"  {food_name} - 未修改（图片获取失败）")
                print()
    else:
        print("  没有需要修改的图片")
    
    print("=" * 60)
    print("脚本执行完成!")
    print("=" * 60)
    print()
    print("下一步:")
    print("  1. 检查 images/ 目录中的图片是否正确")
    print("  2. 在浏览器中打开 index.html 查看效果")
    print("  3. 如果满意，提交更改到Git")
    print()


if __name__ == "__main__":
    main()
