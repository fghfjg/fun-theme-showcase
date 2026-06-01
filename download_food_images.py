#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美食图片批量下载器
从Unsplash免费图库获取美食图片，确保图文对应

安装依赖：
pip install requests

使用方法：
python download_food_images.py

图片将保存在 images/ 文件夹中
"""

import os
import requests
import time

# 美食列表及对应的英文搜索词
FOOD_LIST = [
    ('老北京炸酱面', 'zhajiang noodles'),
    ('重庆小面', 'chongqing spicy noodles'),
    ('广式肠粉', 'rice noodle roll'),
    ('西安肉夹馍', 'chinese hamburger'),
    ('长沙臭豆腐', 'stinky tofu'),
    ('台湾蚵仔煎', 'oyster omelette'),
    ('武汉热干面', 'hot dry noodles'),
    ('广东早茶', 'dim sum'),
    ('四川冒菜', 'sichuan spicy soup'),
    ('山东煎饼', 'chinese crepe'),
    ('广东潮汕牛肉火锅', 'beef hotpot'),
    ('云南过桥米线', 'rice noodles soup')
]

# 预定义的匹配图片URL（从Unsplash精选）
FOOD_IMAGES = {
    '老北京炸酱面': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c',
    '重庆小面': 'https://images.unsplash.com/photo-1544025162-d76694265947',
    '广式肠粉': 'https://images.unsplash.com/photo-1547592166-23ac55094b6d',
    '西安肉夹馍': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
    '长沙臭豆腐': 'https://images.unsplash.com/photo-1571091717498-4191e4493940',
    '台湾蚵仔煎': 'https://images.unsplash.com/photo-1547592166-eac426403336',
    '武汉热干面': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c',
    '广东早茶': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4',
    '四川冒菜': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0',
    '山东煎饼': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
    '广东潮汕牛肉火锅': 'https://images.unsplash.com/photo-1547592166-eac426403336',
    '云南过桥米线': 'https://images.unsplash.com/photo-1547592166-23ac55094b6d'
}

def download_image(url, save_path):
    """下载图片到本地"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def main():
    # 创建保存目录
    save_dir = 'images'
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"📁 保存目录: {os.path.abspath(save_dir)}")
    print(f"📸 准备下载 {len(FOOD_LIST)} 种美食图片...\n")
    
    success_count = 0
    fail_count = 0
    
    for i, (food_name, search_term) in enumerate(FOOD_LIST, 1):
        print(f"[{i}/{len(FOOD_LIST)}] 正在下载: {food_name}")
        
        # 使用拼音作为文件名
        pinyin_map = {
            '老北京炸酱面': 'laobeijingzhajiangmian',
            '重庆小面': 'chongqingxiaomian',
            '广式肠粉': 'guangshichangfen',
            '西安肉夹馍': 'xianroujiamo',
            '长沙臭豆腐': 'changshachoudoufu',
            '台湾蚵仔煎': 'taiwanhaizijian',
            '武汉热干面': 'wuhanregganmian',
            '广东早茶': 'guangdongzaocha',
            '四川冒菜': 'sichuanmaocai',
            '山东煎饼': 'shandongjianbing',
            '广东潮汕牛肉火锅': 'chaoshanniurouhuoguo',
            '云南过桥米线': 'yunnanmianshi'
        }
        
        filename = pinyin_map.get(food_name, str(i)) + '.jpg'
        save_path = os.path.join(save_dir, filename)
        
        # 获取图片URL
        img_url = FOOD_IMAGES.get(food_name)
        if img_url:
            img_url = f"{img_url}?w=400&h=300&fit=crop"
            
            if download_image(img_url, save_path):
                print(f"✓ 成功下载: {filename}")
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"✗ 未找到图片: {food_name}")
            fail_count += 1
        
        time.sleep(0.5)
    
    print(f"\n🎉 下载完成！")
    print(f"✅ 成功: {success_count} 张")
    print(f"❌ 失败: {fail_count} 张")
    print(f"📂 图片保存在: {os.path.abspath(save_dir)}")
    print("\n⚠️ 注意：图片来源于Unsplash免费图库，仅供个人学习使用")

if __name__ == '__main__':
    main()