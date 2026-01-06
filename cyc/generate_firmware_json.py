import os
import json
import hashlib
import re
from collections import defaultdict
from datetime import datetime

def calculate_md5(file_path):
    """计算文件的MD5值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest().lower()

def parse_filename(filename):
    """解析文件名，提取设备类型和变体信息"""
    # 首先检查是否为X-9000 V3
    if 'X9KV3' in filename or 'X-9000V3' in filename.upper():
        device = 'X-9000 V3'
        variant = 'Normal'
        return device, variant
    
    parts = filename.split('-')
    if len(parts) < 3:
        return None, None
    
    # 确定设备类型
    if filename.startswith('X-9000'):
        device = 'X-9000'
        variant = 'B' if 'X-9000B' in filename else 'Normal'
    elif filename.startswith('X6P'):
        device = 'Photon'
        # 确定Photon的变体
        variant_part = parts[2]
        if variant_part == 'OQC':
            variant = 'Normal'
        elif variant_part in ['CO', 'JAPAN', 'EPAC_NO_SHOW_WATTAGE', 'BFE']:
            variant = {'CO': 'CO', 'JAPAN': 'JP', 'EPAC_NO_SHOW_WATTAGE': 'EP', 'BFE': 'BF'}[variant_part]
        else:
            variant = 'Normal'
    elif filename.startswith('X6-'):
        if 'PRO3' in filename:
            device = 'X6 - X1 Pro'
        elif 'STL3' in filename:
            device = 'X6 - X1 Stealth'
        else:
            return None, None
        variant = 'Normal'
    elif filename.startswith('X12-'):
        gen_part = parts[-1].split('.')[0]  # 去掉.bin
        if 'PRO4' in gen_part:
            device = 'X12 Pro Gen 4'
            variant_part = parts[2]
            if variant_part == 'OQC':
                variant = 'Normal' if 'MXPRO4' not in filename else 'MX'
            elif variant_part == 'RS':
                variant = 'RS'
            else:
                variant = 'Normal'
        elif 'PRO3' in gen_part:
            device = 'X12 Pro Gen 3'
            variant = 'Normal'
        else:
            return None, None
    else:
        return None, None
    
    return device, variant

def extract_date(filename):
    """改进的日期提取函数，支持多种日期格式"""
    # 尝试匹配6位数字的日期 (yymmdd)
    date_match = re.search(r'(\d{2})(\d{2})(\d{2})', filename)
    if date_match:
        return f"20{date_match.group(1)}{date_match.group(2)}{date_match.group(3)}"
    
    # 尝试匹配8位数字的日期 (yyyymmdd)
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}{date_match.group(2)}{date_match.group(3)}"
    
    return None

def generate_md5_file(source_file, md5_file):
    """生成MD5校验文件"""
    try:
        md5_value = calculate_md5(source_file)
        with open(md5_file, 'w') as f:
            f.write(f"{md5_value}")
        return True
    except Exception as e:
        print(f"错误: 生成 {md5_file} 时出错: {e}")
        return False

def compare_dates(date1, date2):
    """比较两个日期字符串，返回较新的那个"""
    try:
        dt1 = datetime.strptime(date1, "%Y%m%d")
        dt2 = datetime.strptime(date2, "%Y%m%d")
        return date1 if dt1 >= dt2 else date2
    except ValueError:
        return date1  # 如果无法解析，默认保留第一个

def main():
    # 扫描当前目录下的.bin文件
    bin_files = [f for f in os.listdir('.') if f.endswith('.bin')]
    
    # 创建数据结构
    firmware_data = defaultdict(dict)
    file_info_cache = {}  # 临时存储所有找到的文件信息
    
    for filename in bin_files:
        device, variant = parse_filename(filename)
        if device and variant:
            # 从文件名中提取日期
            formatted_date = extract_date(filename)
            
            if not formatted_date:
                print(f"警告: 无法从文件名 {filename} 中提取日期，将跳过此文件")
                continue
            
            # 计算MD5
            try:
                md5_value = calculate_md5(filename)
            except Exception as e:
                print(f"错误: 计算文件 {filename} 的MD5时出错: {e}")
                continue
            
            # 缓存文件信息
            key = (device, variant)
            if key not in file_info_cache:
                file_info_cache[key] = {
                    "latest": formatted_date,
                    "url": filename,
                    "md5": md5_value
                }
            else:
                # 比较日期，保留较新的
                current_date = file_info_cache[key]["latest"]
                if compare_dates(formatted_date, current_date) == formatted_date:
                    file_info_cache[key] = {
                        "latest": formatted_date,
                        "url": filename,
                        "md5": md5_value
                    }
                    print(f"信息: 发现 {device} {variant} 的更新版本: {filename} (日期: {formatted_date})")
        else:
            print(f"警告: 无法识别文件 {filename} 的设备类型或变体，将跳过此文件")
    
    # 将缓存的数据转移到最终结构中
    for (device, variant), info in file_info_cache.items():
        firmware_data[device][variant] = info
    
    # 转换为JSON并保存
    json_filename = 'firmware.json'
    try:
        with open(json_filename, 'w') as f:
            json.dump(firmware_data, f, indent=2, ensure_ascii=False)
        print(f"JSON文件已生成: {json_filename} (共处理 {len(bin_files)} 个文件，成功 {len(file_info_cache)} 个)")
    except Exception as e:
        print(f"错误: 保存 {json_filename} 时出错: {e}")
        return
    
    # 生成firmware.md5文件
    md5_filename = 'firmware.md5'
    if generate_md5_file(json_filename, md5_filename):
        print(f"MD5校验文件已生成: {md5_filename}")
    else:
        print("警告: 未能生成MD5校验文件")

if __name__ == "__main__":
    main()