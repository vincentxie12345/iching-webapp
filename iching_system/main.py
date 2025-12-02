# iching_system/main.py
"""
易經占卜系統 - 主程式入口
========================

統一的占卜入口，支援所有起卦方式
"""

from typing import Dict, Optional, List
from datetime import datetime

from .config import load_env, check_api_keys
from .core import compute_b_stage, set_data_dir
from .divination import (
    random_divination,
    number_divination,
    questionnaire_divination,
    agent_divination_a4_1
)
from .interpretation import interpret


def divination(
    question: str = None,
    method: str = None,  # 改為 None，自動判斷
    show_original: bool = False,
    save: bool = False,
    interactive: bool = True,
    **kwargs
) -> Dict:
    """
    統一占卜入口
    
    Args:
        question: 問題（可選，互動模式下會詢問）
        method: 起卦方式
            - 'A1': 默禱起卦（不輸入題目，題目在問者心中）
            - 'A2': 隨機起卦（輸入題目）
            - 'A3': 問卷起卦
            - 'A4': Agent 起卦
        show_original: 是否顯示原典
        save: 是否儲存結果
        interactive: 是否互動模式
        **kwargs: 各方式的額外參數
    
    Returns:
        完整占卜結果
    
    Example:
        >>> result = divination()  # 互動式，會詢問問題
        >>> result = divination("該不該跳槽？")  # 自動使用 A2
        >>> result = divination("該不該跳槽？", method='A3')
    """
    
    # 收集問題（如果未提供且為互動模式）
    if not question and interactive:
        question = input("您的問題：").strip()
    
    # 判斷起卦方式
    if method is None:
        if question:
            method = 'A2'  # 有輸入問題 → A2 隨機起卦
        else:
            method = 'A1'  # 沒有輸入問題 → A1 默禱
    
    # 設定顯示用的問題文字
    display_question = question if question else "（默禱，題目在問者心中）"
    
    # 1. 起卦
    if method in ('A1', 'A2'):
        # A1 和 A2 都是隨機起卦，差別只在於是否有輸入問題
        div_result = random_divination(kwargs.get('seed'))
        
    elif method == 'A3':
        div_result = questionnaire_divination(
            question or "請指引方向",
            aspects=kwargs.get('aspects'),
            scores=kwargs.get('scores'),
            interactive=kwargs.get('interactive', True)
        )
        
    elif method == 'A4':
        div_result = agent_divination_a4_1(
            question or "請指引方向",
            description=kwargs.get('description'),
            inner_scores=kwargs.get('inner_scores'),
            interactive=kwargs.get('interactive', True)
        )
        
    else:
        raise ValueError(f"未知的起卦方式: {method}，可用方式: A1, A2, A3, A4")
    
    # 2. 解卦
    # A1 默禱時，使用通用問題文字給 LLM 參考
    interpret_question = question if question else "請指引我目前的狀況與方向"
    
    interpretation = interpret(
        interpret_question,
        div_result['hexagrams'],
        show_original=show_original,
        display=True
    )
    
    # 3. 組合結果
    result = {
        **div_result,
        'question': question,  # 原始問題（A1 默禱時為 None）
        'display_question': display_question,  # 顯示用問題
        'interpret_question': interpret_question,  # 解卦用問題
        'interpretation': interpretation,
        'timestamp': datetime.now().isoformat()
    }
    
    # 4. 儲存
    if save:
        filename = f"divination_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        _save_result(result, filename)
        print(f"\n✅ 結果已儲存至：{filename}")
    
    return result


def _save_result(result: Dict, filename: str):
    """儲存結果到檔案"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("【易經占卜結果】\n")
        f.write("="*70 + "\n\n")
        
        # 使用 display_question（A1 默禱時會顯示「默禱，題目在問者心中」）
        display_q = result.get('display_question') or result.get('question') or ''
        f.write(f"問題：{display_q}\n")
        f.write(f"時間：{result.get('timestamp', '')}\n")
        f.write(f"起卦方式：{result.get('method', '')}\n\n")
        
        f.write(f"六爻數值：{result.get('yao_values', [])}\n")
        f.write(f"本卦：{result['hexagrams']['本卦'].get('name', '')}\n")
        f.write(f"之卦：{result['hexagrams']['之卦'].get('name', '')}\n")
        f.write(f"轉移卦：{result['hexagrams']['轉移卦'].get('name', '')}\n\n")
        
        f.write("="*70 + "\n")
        f.write("【解卦】\n")
        f.write("="*70 + "\n\n")
        
        interp = result.get('interpretation', {})
        for key in ['1_現況', '2_變化趨勢', '3_變化過程', '4_六爻境遇', '5_建議', '6_展望']:
            if key in interp:
                title = key.split('_')[1]
                f.write(f"【{title}】\n")
                f.write(interp[key] + "\n\n")
        
        f.write("="*70 + "\n")


# 便捷函數
def quick_divination(question: str, **kwargs) -> Dict:
    """快速占卜（A2 隨機，有輸入問題）"""
    return divination(question, method='A2', **kwargs)


def questionnaire(question: str, **kwargs) -> Dict:
    """問卷占卜（A3）"""
    return divination(question, method='A3', **kwargs)


def agent(question: str, **kwargs) -> Dict:
    """Agent 占卜（A4）"""
    return divination(question, method='A4', **kwargs)


# 初始化
def init(data_dir: Optional[str] = None, env_path: Optional[str] = None):
    """
    初始化系統
    
    Args:
        data_dir: 資料目錄路徑
        env_path: .env 檔案路徑
    """
    # 載入環境變數
    load_env(env_path)
    
    # 設定資料目錄
    if data_dir:
        set_data_dir(data_dir)
    
    # 檢查 API Keys
    check_api_keys()
    
    print("\n✅ 易經占卜系統已初始化")
    print("\n使用方式：")
    print("  from iching_system import divination, quick_divination")
    print("  result = divination()  # 互動式，自動判斷 A1/A2")
    print("  result = quick_divination('該不該跳槽？')  # A2 隨機起卦")
