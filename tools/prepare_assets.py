#!/usr/bin/env python3
"""
tools/prepare_assets.py
ユーザー提供素材（assets 2/instagram/）から採用写真・動画を選定し、
WebP変換・リサイズ・メタデータ生成を行い assets/media/ に配置する。
原本（assets 2/）は一切変更しない。
"""

import os
import shutil
import json
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_INSTA_DIR = os.path.join(BASE_DIR, "assets 2", "instagram")
SRC_MANIFEST = os.path.join(SRC_INSTA_DIR, "manifest.json")
DST_MEDIA_DIR = os.path.join(BASE_DIR, "assets", "media")

os.makedirs(DST_MEDIA_DIR, exist_ok=True)

with open(SRC_MANIFEST, "r", encoding="utf-8") as f:
    insta_data = json.load(f)

# インスタmanifestから投稿情報を引く辞書を作成
posts_by_file = {}
for post in insta_data.get("items", []):
    for fn in post.get("files", []):
        posts_by_file[fn] = post

SELECTED_IMAGES = [
    {
        "id": "hero_gold",
        "src_rel": "images/p29_DFmGQ90Ca2G.jpg",
        "role": "トップヒーロー背景（黄金の舞台光と太鼓）",
        "alt": "黄金色の舞台照明を浴びて和太鼓に向き合う韮崎工業高校太鼓部の演奏風景",
        "crops": [
            {"suffix": "-large", "width": 1600, "quality": 82},
            {"suffix": "-medium", "width": 1080, "quality": 82},
            {"suffix": "-small", "width": 720, "quality": 80},
        ],
    },
    {
        "id": "stage_geibunsai",
        "src_rel": "images/p04_DR1IAKdEmFd_01.jpg",
        "role": "芸術文化祭 舞台全景（部紹介・活動記録）",
        "alt": "芸術文化祭の舞台上で太鼓が整然と並び演奏が繰り広げられる全景",
        "crops": [
            {"suffix": "-1000", "width": 1000, "quality": 80},
            {"suffix": "-600", "width": 600, "quality": 78},
        ],
    },
    {
        "id": "odaiko_back",
        "src_rel": "images/p15_DNzwjqN5FzT_01.jpg",
        "role": "関東大会 大太鼓と背中（天野流の魂・気迫）",
        "alt": "大太鼓に向かって力強くバチを構える太鼓部員の背中",
        "crops": [
            {"suffix": "-1000", "width": 1000, "quality": 80},
            {"suffix": "-600", "width": 600, "quality": 78},
        ],
    },
    {
        "id": "stage_kanto",
        "src_rel": "images/p15_DNzwjqN5FzT_03.jpg",
        "role": "関東大会 正面演奏の瞬間（実績・演奏）",
        "alt": "関東地区高等学校和太鼓選手権での熱のこもった正面演奏の瞬間",
        "crops": [
            {"suffix": "-1000", "width": 1000, "quality": 80},
            {"suffix": "-600", "width": 600, "quality": 78},
        ],
    },
    {
        "id": "festival_night",
        "src_rel": "images/p23_DKma7SOSwz7_01.jpg",
        "role": "小田川ホタルまつり 夜間野外演奏（地域交流）",
        "alt": "小田川ホタルまつりの夜間野外ステージで提灯の明かりに照らされ太鼓を叩く部員たち",
        "crops": [
            {"suffix": "-1000", "width": 1000, "quality": 80},
            {"suffix": "-600", "width": 600, "quality": 78},
        ],
    },
    {
        "id": "community_stage",
        "src_rel": "images/p21_DLcc5UxSDJa_01.jpg",
        "role": "北杜市ふれあい塾 交流演奏（活動の広がり・リンク集）",
        "alt": "北杜市ふれあい塾での生き生きとした地域交流演奏の様子",
        "crops": [
            {"suffix": "-1000", "width": 1000, "quality": 80},
            {"suffix": "-600", "width": 600, "quality": 78},
        ],
    },
    {
        "id": "practice_bachi",
        "src_rel": "images/p05_DRo1ST_EvPR_01.jpg",
        "role": "合同練習会 バチと練習風景（紹介・動画ページ）",
        "alt": "定期演奏会に向けた合同練習会でバチを手に真剣に向き合う部員たち",
        "crops": [
            {"suffix": "-1000", "width": 1000, "quality": 80},
            {"suffix": "-600", "width": 600, "quality": 78},
        ],
    },
]

SELECTED_VIDEO = {
    "id": "practice_clip",
    "src_rel_video": "videos/p14_DOjAD-tkskX_03.mp4",
    "src_rel_poster": "videos/p14_DOjAD-tkskX_03_poster.jpg",
    "dst_video_name": "clip-practice.mp4",
    "role": "合同練習ショートクリップ（動画ギャラリー内、公式提供映像）",
    "title": "合同練習での響き（公式Instagramより提供）",
    "alt_poster": "太鼓部合同練習会の動画ポスター",
}

manifest_output = {
    "source_archive": "assets 2/instagram",
    "generated_at": "2026-09-12",
    "images": [],
    "videos": []
}

for item in SELECTED_IMAGES:
    src_abs = os.path.join(SRC_INSTA_DIR, item["src_rel"])
    if not os.path.exists(src_abs):
        print(f"Warning: {src_abs} not found!")
        continue
    
    post_info = posts_by_file.get(item["src_rel"], {})
    
    with Image.open(src_abs) as img:
        orig_w, orig_h = img.size
        orig_aspect = orig_w / orig_h
        
        variants = []
        for crop in item["crops"]:
            target_w = crop["width"]
            if target_w >= orig_w:
                target_w = orig_w
            target_h = int(target_w / orig_aspect)
            
            resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            dst_fn = f"{item['id']}{crop['suffix']}.webp"
            dst_path = os.path.join(DST_MEDIA_DIR, dst_fn)
            resized.save(dst_path, "WEBP", quality=crop["quality"], method=6)
            
            size_kb = round(os.path.getsize(dst_path) / 1024, 1)
            variants.append({
                "filename": dst_fn,
                "width": target_w,
                "height": target_h,
                "size_kb": size_kb
            })
            print(f"Generated {dst_fn}: {target_w}x{target_h} ({size_kb} KB)")

        manifest_output["images"].append({
            "id": item["id"],
            "role": item["role"],
            "alt": item["alt"],
            "original_path": item["src_rel"],
            "original_dimensions": {"width": orig_w, "height": orig_h},
            "post_url": post_info.get("url"),
            "post_code": post_info.get("code"),
            "variants": variants
        })

# 動画とポスターの処理
src_vid_abs = os.path.join(SRC_INSTA_DIR, SELECTED_VIDEO["src_rel_video"])
src_post_abs = os.path.join(SRC_INSTA_DIR, SELECTED_VIDEO["src_rel_poster"])

if os.path.exists(src_vid_abs):
    dst_vid_path = os.path.join(DST_MEDIA_DIR, SELECTED_VIDEO["dst_video_name"])
    shutil.copy2(src_vid_abs, dst_vid_path)
    vid_size_kb = round(os.path.getsize(dst_vid_path) / 1024, 1)
    
    post_info = posts_by_file.get(SELECTED_VIDEO["src_rel_video"], {})
    
    poster_variants = []
    if os.path.exists(src_post_abs):
        with Image.open(src_post_abs) as pimg:
            pw, ph = pimg.size
            dst_poster_fn = f"{SELECTED_VIDEO['id']}-poster.webp"
            dst_poster_path = os.path.join(DST_MEDIA_DIR, dst_poster_fn)
            pimg.save(dst_poster_path, "WEBP", quality=80)
            poster_size_kb = round(os.path.getsize(dst_poster_path) / 1024, 1)
            poster_variants.append({
                "filename": dst_poster_fn,
                "width": pw,
                "height": ph,
                "size_kb": poster_size_kb
            })
            print(f"Generated {dst_poster_fn}: {pw}x{ph} ({poster_size_kb} KB)")
            
    manifest_output["videos"].append({
        "id": SELECTED_VIDEO["id"],
        "filename": SELECTED_VIDEO["dst_video_name"],
        "size_kb": vid_size_kb,
        "role": SELECTED_VIDEO["role"],
        "title": SELECTED_VIDEO["title"],
        "original_path": SELECTED_VIDEO["src_rel_video"],
        "post_url": post_info.get("url"),
        "post_code": post_info.get("code"),
        "poster": poster_variants
    })
    print(f"Copied video {SELECTED_VIDEO['dst_video_name']} ({vid_size_kb} KB)")

manifest_path = os.path.join(DST_MEDIA_DIR, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest_output, f, ensure_ascii=False, indent=2)

print(f"Assets prepared successfully! Manifest written to {manifest_path}")
