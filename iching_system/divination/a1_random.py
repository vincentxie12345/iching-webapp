# iching_system/divination/a1_random.py
"""
A1 隨機起卦
===========
使用大衍筮法隨機生成六爻

這是最基本的起卦方式，完全依賴隨機數。
適合：一般占卜、快速起卦
"""

from typing import Optional, Dict
from ..core.dayan import dayan_six_yao, get_yao_name
from ..core.calculator import compute_b_stage


def random_divination(seed: Optional[int] = None) -> Dict:
    """
    A1 隨機起卦
    
    使用大衍筮法生成六爻，然後計算本卦、之卦、轉移卦
    
    Args:
        seed: 隨機種子（可選，用於重現結果）
    
    Returns:
        {
            'method': 'A1',
            'method_name': '隨機起卦',
            'seed': seed,
            'yao_values': [7, 8, 9, 6, 7, 8],
            'yao_names': ['少陽', '少陰', ...],
            'hexagrams': {
                '本卦': {...},
                '之卦': {...},
                '轉移卦': {...},
                '動爻': [...],
                '動爻數': 2
            }
        }
    
    Example:
        >>> result = random_divination()
        >>> print(result['hexagrams']['本卦']['name'])
        乾
    """
    # 生成六爻
    yao_values = dayan_six_yao(seed)
    
    # 計算卦象
    hexagrams = compute_b_stage(yao_values)
    
    # 組合結果
    return {
        'method': 'A1',
        'method_name': '隨機起卦',
        'seed': seed,
        'yao_values': yao_values,
        'yao_names': [get_yao_name(y) for y in yao_values],
        'hexagrams': hexagrams
    }


def quick_random(seed: Optional[int] = None) -> Dict:
    """
    快速隨機起卦（簡化版）
    
    Returns:
        只包含基本資訊的字典
    """
    result = random_divination(seed)
    
    return {
        'yao': result['yao_values'],
        'now': result['hexagrams']['本卦']['name'],
        'target': result['hexagrams']['之卦']['name'],
        'trans': result['hexagrams']['轉移卦']['name']
    }


def interactive_random_divination(question: str = None) -> Dict:
    """
    互動式隨機起卦
    
    包含：收集問題 → 隨機起卦
    
    Args:
        question: 問題（可選，不提供則互動詢問）
    
    Returns:
        起卦結果
    """
    print("="*60)
    print("【A1 隨機起卦】")
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
    
    print("\n正在起卦（大衍筮法）...")
    
    # 隨機起卦
    result = random_divination()
    result['question'] = question
    
    print(f"\n✓ 起卦完成")
    print(f"六爻數值：{result['yao_values']}")
    print(f"六爻意義：{result['yao_names']}")
    print(f"本卦：{result['hexagrams']['本卦']['name']}")
    print(f"之卦：{result['hexagrams']['之卦']['name']}")
    print(f"轉移卦：{result['hexagrams']['轉移卦']['name']}")
    print("="*60)
    
    return result
