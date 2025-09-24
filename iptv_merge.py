#!/usr/bin/env python3
import requests
import re
import os

# 源地址列表
M3U_URLS = [
    # 全球
    "https://iptv-org.github.io/iptv/index.m3u",
    #"https://raw.githubusercontent.com/dongyubin/IPTV/main/IPTV.m3u",
    # 中国
    "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
    #"https://raw.githubusercontent.com/xiaoxiaozhou-zcx/IPTV/main/iptv.m3u"
]

OUTPUT_ALL = "merged.m3u"
OUTPUT_DIR = "output_m3u"   # 分类文件输出目录

def download_m3u(url):
    try:
        print(f"Downloading: {url}")
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return ""

def parse_m3u(content):
    """解析 M3U 文件，返回频道列表 (name, link, group, country)"""
    entries = []
    lines = content.splitlines()
    name, group, country = None, "Other", "Unknown"

    for line in lines:
        if line.startswith("#EXTINF"):
            # 频道名
            m_name = re.search(r'tvg-name="?(.*?)"?(,|$)', line)
            if m_name:
                name = m_name.group(1).strip()
            else:
                if "," in line:
                    name = line.split(",")[-1].strip()

            # 分组 group-title
            m_group = re.search(r'group-title="(.*?)"', line)
            if m_group:
                group = m_group.group(1).strip()
            else:
                group = "Other"

            # 国家代码 tvg-country
            m_country = re.search(r'tvg-country="(.*?)"', line)
            if m_country:
                country = m_country.group(1).upper()
            else:
                country = "Unknown"

        elif line.startswith("http"):
            if name:
                entries.append((name, line.strip(), group, country))
                name, group, country = None, "Other", "Unknown"
    return entries

def save_m3u(filename, entries):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, link, group, country in entries:
            f.write(f'#EXTINF:-1 group-title="{group}",{name}\n{link}\n')

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_entries = {}

    # 下载 + 解析
    for url in M3U_URLS:
        content = download_m3u(url)
        if not content:
            continue
        entries = parse_m3u(content)
        for name, link, group, country in entries:
            if name not in all_entries:
                all_entries[name] = (name, link, group, country)

    entries_list = list(all_entries.values())
    print(f"Total merged channels: {len(entries_list)}")

    # 输出全集
    save_m3u(OUTPUT_ALL, entries_list)
    print(f"✅ Full list saved to {OUTPUT_ALL}")

    # 按 group 分类
    group_map = {}
    for e in entries_list:
        group_map.setdefault(e[2], []).append(e)

    for group, items in group_map.items():
        filename = os.path.join(OUTPUT_DIR, f"group_{group.replace(' ', '_')}.m3u")
        save_m3u(filename, items)
    print(f"✅ Group files saved in {OUTPUT_DIR}/")

    # 按国家分类
    country_map = {}
    for e in entries_list:
        country_map.setdefault(e[3], []).append(e)

    for country, items in country_map.items():
        filename = os.path.join(OUTPUT_DIR, f"{country}.m3u")
        save_m3u(filename, items)
    print(f"✅ Country files saved in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()

