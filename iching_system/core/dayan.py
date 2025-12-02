# iching_system/core/dayan.py
"""
大衍筮法核心
============
易經起卦的最基礎算法，所有起卦方式都依賴此模組

大衍之數五十，其用四十有九。
分而為二以象兩，掛一以象三，
揲之以四以象四時，歸奇於扐以象閏。
"""

import random
from typing import List, Optional


def _change_once(total: int, rng: random.Random) -> int:
    """
    大衍筮法的一變
    
    Args:
        total: 當前籌策總數
        rng: 隨機數生成器
    
    Returns:
        經過一變後剩餘的籌策數
    """
    # 分而為二以象兩
    left = rng.randint(1, total - 1)
    right = total - left
    
    # 掛一以象三
    right -= 1
    
    # 揲之以四以象四時
    left_remainder = left % 4 or 4
    right_remainder = right % 4 or 4
    
    # 歸奇於扐以象閏
    return total - left_remainder - right_remainder - 1


def _generate_one_yao(rng: random.Random) -> int:
    """
    生成一爻（三變成一爻）
    
    Returns:
        6（老陰）、7（少陽）、8（少陰）、9（老陽）
    """
    total = 49  # 大衍之數五十，其用四十有九
    
    # 三變
    total = _change_once(total, rng)
    total = _change_once(total, rng)
    total = _change_once(total, rng)
    
    # 計算爻值
    yao_map = {24: 9, 28: 8, 32: 7, 36: 6}
    return yao_map.get(total, 7)  # 預設少陽


def dayan_six_yao(seed: Optional[int] = None) -> List[int]:
    """
    大衍筮法生成六爻
    
    Args:
        seed: 隨機種子（可選，用於重現結果）
    
    Returns:
        六爻陰陽值列表 [6/7/8/9 × 6]
        - 6: 老陰（變爻，陰→陽）
        - 7: 少陽（靜爻，陽）
        - 8: 少陰（靜爻，陰）
        - 9: 老陽（變爻，陽→陰）
    
    Example:
        >>> dayan_six_yao(42)
        [7, 8, 7, 9, 6, 7]
    """
    rng = random.Random(seed)
    return [_generate_one_yao(rng) for _ in range(6)]


def yao_to_bit(yao: int) -> int:
    """
    爻值轉二進位
    
    Args:
        yao: 爻值（6/7/8/9）
    
    Returns:
        0（陰）或 1（陽）
        - 6（老陰）、8（少陰）→ 0
        - 7（少陽）、9（老陽）→ 1
    """
    return 0 if yao in (6, 8) else 1


def bits_to_code(bits: List[int]) -> str:
    """
    二進位列表轉卦碼字串
    
    Args:
        bits: [0, 1, 1, 0, 1, 1]
    
    Returns:
        "011011"
    """
    return ''.join(str(b) for b in bits)


def code_to_bits(code: str) -> List[int]:
    """
    卦碼字串轉二進位列表
    
    Args:
        code: "011011"
    
    Returns:
        [0, 1, 1, 0, 1, 1]
    """
    return [int(c) for c in code]


def is_moving_line(yao: int) -> bool:
    """
    判斷是否為動爻
    
    Args:
        yao: 爻值（6/7/8/9）
    
    Returns:
        True if 動爻（6 或 9）
    """
    return yao in (6, 9)


def get_moving_lines(yao_values: List[int]) -> List[int]:
    """
    取得動爻位置
    
    Args:
        yao_values: 六爻值列表
    
    Returns:
        動爻位置列表（0-5）
    """
    return [i for i, y in enumerate(yao_values) if is_moving_line(y)]


def flip_bit(bit: int) -> int:
    """翻轉一個 bit"""
    return 1 - bit


def flip_line(code: str, line_index: int) -> str:
    """
    翻轉指定爻位
    
    Args:
        code: 卦碼 "111111"
        line_index: 爻位索引（0-5，從初爻開始）
    
    Returns:
        翻轉後的卦碼
    """
    bits = code_to_bits(code)
    bits[line_index] = flip_bit(bits[line_index])
    return bits_to_code(bits)


# 分數轉爻值（A3/A4 使用）
def score_to_yao(score: int) -> int:
    """
    將分數（0-10）轉換成陰陽值（6/7/8/9）
    
    分數映射邏輯：
    - 0, 1, 2 分 → 8 (老陰，積重難返 - 太弱，很難改變)
    - 3, 4, 5 分 → 6 (少陰，易反 - 不夠好，有向上張力)
    - 6, 7, 8 分 → 7 (少陽，初發向上 - 不錯，正在成長)
    - 9, 10 分   → 9 (老陽，強弩之末易墜 - 太強，物極必反)
    
    物理直覺：
    - 很弱 → 老陰（沉重，難以改變）
    - 偏弱 → 少陰（有反彈向上的表面張力）
    - 偏強 → 少陽（順勢成長中）
    - 很強 → 老陽（到頂了，容易往下）
    """
    if score <= 2:
        return 8  # 老陰：積重難返
    elif score <= 5:
        return 6  # 少陰：易反
    elif score <= 8:
        return 7  # 少陽：初發向上
    else:  # 9-10
        return 9  # 老陽：強弩之末易墜


# 爻值名稱
YAO_NAMES = {
    6: "少陰(易反)",
    7: "少陽(初發向上)",
    8: "老陰(積重難返)",
    9: "老陽(強弩之末)"
}

def get_yao_name(yao: int) -> str:
    """取得爻值名稱"""
    return YAO_NAMES.get(yao, "未知")
