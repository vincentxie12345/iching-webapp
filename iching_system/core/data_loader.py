# iching_system/core/data_loader.py
"""
資料載入器
==========
載入並管理易經 JSON 資料檔

支援三個版本：
- original: i_ching.json（原典）
- modern: i_ching_modern.json（Modern 1）
- modern2: i_ching_modern2.json（Modern 2，主要使用）
"""

import json
import os
from typing import Dict, Optional, Any
from pathlib import Path


# 資料快取
_DATA_CACHE: Dict[str, Dict] = {}

# 資料目錄
_DATA_DIR: Optional[str] = None


def set_data_dir(path: str):
    """設定資料目錄路徑"""
    global _DATA_DIR
    _DATA_DIR = path


def get_data_dir() -> str:
    """取得資料目錄路徑"""
    global _DATA_DIR
    
    if _DATA_DIR:
        return _DATA_DIR
    
    # 自動偵測
    possible_paths = [
        Path(__file__).parent.parent / 'data',  # 相對於此檔案
        Path.cwd() / 'data',  # 當前目錄
        Path.cwd() / 'iching_system' / 'data',
        Path.home() / 'pyprogram' / 'iching_system' / 'data',
        Path('/mnt/project'),  # Claude 環境
    ]
    
    for path in possible_paths:
        if path.exists() and (path / 'i_ching_modern2.json').exists():
            _DATA_DIR = str(path)
            return _DATA_DIR
    
    raise FileNotFoundError("找不到資料目錄，請使用 set_data_dir() 設定")


def _get_filename(version: str) -> str:
    """取得版本對應的檔案名"""
    filename_map = {
        'original': 'i_ching.json',
        'modern': 'i_ching_modern.json',
        'modern2': 'i_ching_modern2.json'
    }
    
    if version not in filename_map:
        raise ValueError(f"未知的版本: {version}，可用版本: {list(filename_map.keys())}")
    
    return filename_map[version]


def load_data(version: str = 'modern2') -> Dict:
    """
    載入易經資料
    
    Args:
        version: 'original' | 'modern' | 'modern2'
    
    Returns:
        完整的易經資料字典
    """
    global _DATA_CACHE
    
    if version in _DATA_CACHE:
        return _DATA_CACHE[version]
    
    data_dir = get_data_dir()
    filename = _get_filename(version)
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"找不到資料檔: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 自動修復編碼問題（UTF-8 字元被錯誤以 Latin-1 保存）
    data = _fix_encoding(data)
    
    _DATA_CACHE[version] = data
    
    return _DATA_CACHE[version]


def _fix_encoding(obj):
    """
    遞迴修復字典/列表中的字串編碼
    解決 UTF-8 字元被當成 Latin-1 保存的問題
    """
    if isinstance(obj, str):
        if not obj:
            return obj
        try:
            # 嘗試修復：latin-1 → utf-8
            fixed = obj.encode('latin-1').decode('utf-8')
            return fixed
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        try:
            # 嘗試 cp1252
            fixed = obj.encode('cp1252').decode('utf-8')
            return fixed
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        try:
            # 嘗試 iso-8859-1
            fixed = obj.encode('iso-8859-1').decode('utf-8')
            return fixed
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        return obj
    elif isinstance(obj, dict):
        return {_fix_encoding(k): _fix_encoding(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_fix_encoding(item) for item in obj]
    else:
        return obj


def clear_cache():
    """清除資料快取（用於重新載入）"""
    global _DATA_CACHE
    _DATA_CACHE = {}


def get_hexagram(code: str, version: str = 'modern2') -> Dict:
    """
    取得卦象資料
    
    Args:
        code: 卦碼（如 "111111"）
        version: 資料版本
    
    Returns:
        卦象資料字典
    """
    data = load_data(version)
    
    # 嘗試不同的 key 格式
    if code in data:
        return data[code]
    
    # 有些資料可能用卦名作 key
    for key, value in data.items():
        if isinstance(value, dict) and value.get('code') == code:
            return value
    
    return {'code': code, 'name': '未知', 'error': f'找不到卦碼 {code}'}


def get_hexagram_by_name(name: str, version: str = 'modern2') -> Optional[Dict]:
    """
    用卦名取得卦象資料
    
    Args:
        name: 卦名（如 "乾"、"坤"）
        version: 資料版本
    
    Returns:
        卦象資料字典
    """
    data = load_data(version)
    
    for key, value in data.items():
        if isinstance(value, dict):
            if value.get('name') == name or value.get('name', '').startswith(name):
                return value
    
    return None


def get_original_text(code: str) -> Dict:
    """
    取得原典文本
    
    Args:
        code: 卦碼
    
    Returns:
        原典資料（卦辭、爻辭等）
    """
    return get_hexagram(code, version='original')


def get_line_text(code: str, line_index: int, version: str = 'modern2') -> Dict:
    """
    取得特定爻的資料
    
    Args:
        code: 卦碼
        line_index: 爻位索引（0-5，從初爻開始）
        version: 資料版本
    
    Returns:
        該爻的資料
    """
    hex_data = get_hexagram(code, version)
    
    # 不同版本可能有不同的爻資料結構
    lines = hex_data.get('lines', hex_data.get('爻辭', []))
    
    if isinstance(lines, list) and len(lines) > line_index:
        return lines[line_index]
    elif isinstance(lines, dict):
        line_names = ['初', '二', '三', '四', '五', '上']
        line_key = line_names[line_index]
        return lines.get(line_key, {})
    
    return {}


def get_all_hexagram_codes() -> list:
    """取得所有卦碼列表"""
    data = load_data('modern2')
    codes = []
    
    for key, value in data.items():
        if isinstance(value, dict) and 'code' in value:
            codes.append(value['code'])
        elif len(key) == 6 and all(c in '01' for c in key):
            codes.append(key)
    
    return sorted(set(codes))


def clear_cache():
    """清除資料快取"""
    global _DATA_CACHE
    _DATA_CACHE = {}


# 便捷函數
def hex_by_code(code: str) -> Dict:
    """快捷方式：取得卦象（使用 modern2）"""
    return get_hexagram(code, 'modern2')


def hex_original(code: str) -> Dict:
    """快捷方式：取得原典"""
    return get_hexagram(code, 'original')
