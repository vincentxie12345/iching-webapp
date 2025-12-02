# iching_system/divination/a2_number.py
"""
A2 報數起卦
===========
用戶報數轉換成卦象

用戶報一個數字，用作大衍筮法的隨機種子。
適合：有靈感時、想用特定數字起卦
"""

from typing import Dict, Optional, Union
from ..core.dayan import dayan_six_yao, get_yao_name
from ..core.calculator import compute_b_stage


def number_divination(number: Union[int, str]) -> Dict:
    """
    A2 報數起卦
    
    用報的數字作為隨機種子進行起卦
    
    Args:
        number: 用戶報的數字（可以是整數或字串）
    
    Returns:
        {
            'method': 'A2',
            'method_name': '報數起卦',
            'number': 123,
            'yao_values': [7, 8, 9, 6, 7, 8],
            'yao_names': ['少陽', '少陰', ...],
            'hexagrams': {...}
        }
    
    Example:
        >>> result = number_divination(168)
        >>> print(result['hexagrams']['本卦']['name'])
    """
    # 轉換成整數
    if isinstance(number, str):
        # 如果是字串，嘗試轉換
        try:
            number = int(number)
        except ValueError:
            # 如果無法轉換，用字串的 hash
            number = hash(number)
    
    # 用報數作為種子
    yao_values = dayan_six_yao(seed=number)
    
    # 計算卦象
    hexagrams = compute_b_stage(yao_values)
    
    return {
        'method': 'A2',
        'method_name': '報數起卦',
        'number': number,
        'yao_values': yao_values,
        'yao_names': [get_yao_name(y) for y in yao_values],
        'hexagrams': hexagrams
    }


def time_divination(use_microseconds: bool = True) -> Dict:
    """
    時間起卦（A2 變體）
    
    用當前時間作為種子
    
    Args:
        use_microseconds: 是否使用微秒（更隨機）
    
    Returns:
        起卦結果
    """
    import time
    
    if use_microseconds:
        number = int(time.time() * 1000000)
    else:
        number = int(time.time())
    
    result = number_divination(number)
    result['method_name'] = '時間起卦'
    result['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    return result


def name_divination(name: str) -> Dict:
    """
    姓名起卦（A2 變體）
    
    用姓名的 hash 作為種子
    
    Args:
        name: 姓名或任意字串
    
    Returns:
        起卦結果
    """
    # 使用更穩定的 hash 方式
    number = sum(ord(c) * (i + 1) for i, c in enumerate(name))
    
    result = number_divination(number)
    result['method_name'] = '姓名起卦'
    result['name'] = name
    
    return result


def interactive_number_divination(question: str = None) -> Dict:
    """
    互動式報數起卦
    
    提示用戶輸入問題和數字
    
    Args:
        question: 問題（可選，不提供則互動詢問）
    """
    print("="*60)
    print("【A2 報數起卦】")
    print("="*60)
    
    # 收集問題
    if not question:
        print("\n請輸入您的問題：")
        print("（例如：今年運勢如何？該不該跳槽？）")
        question = input("→ ").strip()
        if not question:
            question = "請指引方向"
    
    print(f"\n✓ 問題：{question}")
    print("-"*60)
    
    # 收集數字
    print("\n請報一個數字（任意整數）：")
    print("（可以是您當下想到的數字、生日、幸運數字等）")
    
    while True:
        try:
            number_str = input("→ ").strip()
            number = int(number_str)
            break
        except ValueError:
            print("請輸入有效的數字")
    
    result = number_divination(number)
    result['question'] = question
    
    print(f"\n✓ 已記錄：{number}")
    print(f"六爻數值：{result['yao_values']}")
    print(f"本卦：{result['hexagrams']['本卦']['name']}")
    print(f"之卦：{result['hexagrams']['之卦']['name']}")
    print("="*60)
    
    return result
