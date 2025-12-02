# iching_system/divination/a3_questionnaire.py
"""
A3 問卷起卦
===========
透過六個評估問題收集分數，轉換成六爻

內三爻（1-3）：問者內在狀態
外三爻（4-6）：外部環境條件

適合：深度自我探索、問自己的問題
"""

from typing import List, Dict, Optional, Callable
from ..core.dayan import score_to_yao, get_yao_name
from ..core.calculator import compute_b_stage


# 預設的六個評估面向（通用版）
DEFAULT_ASPECTS = {
    "career": {
        "name": "職涯決策",
        "aspects": [
            "關於這個決定的內在動機，是否因為真心想要改變而非逃避現狀",
            "關於個人現有的專業技能、工作經驗、人脈資源是否足以支撐這個決定",
            "關於這個決定後的學習成長空間、職涯發展潛力，以及可能面臨的風險",
            "關於家人朋友的支持態度、新環境的文化氛圍和基本工作條件",
            "關於目前在相關領域的實際表現、他人評價和市場競爭力",
            "關於所處行業的未來發展趨勢、就業市場變化和經濟大環境走向"
        ]
    },
    "relationship": {
        "name": "感情決策",
        "aspects": [
            "關於這段感情中的內心真實感受，是否出於真心想要經營",
            "關於自己在感情中的付出能力、溝通技巧和情緒管理成熟度",
            "關於這段關係的成長空間、長期發展潛力，以及可能的挑戰",
            "關於雙方家庭的態度、朋友圈的看法和基本生活條件的匹配度",
            "關於目前感情的實際互動品質、雙方的投入程度和默契度",
            "關於社會環境對這段感情的影響、價值觀的變遷和長期相處趨勢"
        ]
    },
    "general": {
        "name": "一般決策",
        "aspects": [
            "關於這個決定的內在動機和真實意願強度",
            "關於現有的資源、能力和準備程度",
            "關於這個決定的發展潛力和可能風險",
            "關於周圍環境的支持程度和基本條件",
            "關於目前的實際狀況和外界反應",
            "關於大環境趨勢和長期發展前景"
        ]
    }
}


def classify_question(question: str) -> str:
    """
    分類問題類型
    
    Args:
        question: 用戶的問題
    
    Returns:
        問題類型（career/relationship/general）
    """
    career_keywords = ['工作', '跳槽', '職業', '創業', '升遷', '加薪', '辭職', '轉職', '求職']
    relationship_keywords = ['感情', '愛情', '結婚', '分手', '交往', '對象', '另一半', '男友', '女友']
    
    for kw in career_keywords:
        if kw in question:
            return 'career'
    
    for kw in relationship_keywords:
        if kw in question:
            return 'relationship'
    
    return 'general'


def get_aspects_for_question(question: str, custom_aspects: Optional[List[str]] = None) -> List[str]:
    """
    取得問題對應的六個評估面向
    
    Args:
        question: 用戶的問題
        custom_aspects: 自訂面向（可選）
    
    Returns:
        六個評估面向的描述
    """
    if custom_aspects and len(custom_aspects) == 6:
        return custom_aspects
    
    q_type = classify_question(question)
    return DEFAULT_ASPECTS[q_type]['aspects']


def questionnaire_divination(
    question: str,
    aspects: Optional[List[str]] = None,
    scores: Optional[List[int]] = None,
    interactive: bool = True
) -> Dict:
    """
    A3 問卷起卦
    
    Args:
        question: 用戶的問題
        aspects: 自訂的六個評估面向（可選）
        scores: 預設的六個分數（可選，用於測試）
        interactive: 是否互動式收集分數
    
    Returns:
        {
            'method': 'A3',
            'method_name': '問卷起卦',
            'question': '...',
            'aspects': [...],
            'scores': [7, 8, 5, 6, 7, 8],
            'yao_values': [7, 7, 6, 7, 7, 7],
            'yao_names': [...],
            'hexagrams': {...}
        }
    """
    # 取得評估面向
    aspect_list = get_aspects_for_question(question, aspects)
    
    # 收集分數
    if scores and len(scores) == 6:
        score_list = scores
    elif interactive:
        score_list = _collect_scores_interactive(question, aspect_list)
    else:
        raise ValueError("需要提供 scores 或設定 interactive=True")
    
    # 轉換成爻值
    yao_values = [score_to_yao(s) for s in score_list]
    
    # 計算卦象
    hexagrams = compute_b_stage(yao_values)
    
    return {
        'method': 'A3',
        'method_name': '問卷起卦',
        'question': question,
        'question_type': classify_question(question),
        'aspects': aspect_list,
        'scores': score_list,
        'yao_values': yao_values,
        'yao_names': [get_yao_name(y) for y in yao_values],
        'hexagrams': hexagrams
    }


def _collect_scores_interactive(question: str, aspects: List[str]) -> List[int]:
    """
    互動式收集六個分數
    """
    print("="*70)
    print("【A3 問卷起卦】")
    print("="*70)
    print(f"問題：{question}")
    print("-"*70)
    print("請根據您的實際情況，為以下六個面向打分（0-10分）")
    print("0=非常弱/不足，10=非常強/充足")
    print("="*70)
    
    scores = []
    
    for i, aspect in enumerate(aspects):
        yao_type = "內三爻" if i < 3 else "外三爻"
        
        print(f"\n【第 {i+1} 題 / 共 6 題】({yao_type})")
        print(f"{aspect}")
        print("（0=非常弱/不足，10=非常強/充足）")
        
        while True:
            try:
                score_str = input("您的評分：").strip()
                score = int(score_str)
                if 0 <= score <= 10:
                    break
                else:
                    print("請輸入 0-10 之間的數字")
            except ValueError:
                print("請輸入有效的數字")
        
        yao = score_to_yao(score)
        print(f"✓ 已記錄：{score} 分 → {yao} {get_yao_name(yao)}")
        scores.append(score)
    
    print("\n" + "-"*70)
    print("✓ 問卷完成")
    print(f"六題分數：{scores}")
    print(f"六爻數值：{[score_to_yao(s) for s in scores]}")
    print("="*70)
    
    return scores


def interactive_questionnaire_divination(question: str = None) -> Dict:
    """
    互動式問卷起卦（完整流程）
    
    包含：收集問題 → 顯示六個面向 → 逐題評分
    
    Args:
        question: 問題（可選，不提供則互動詢問）
    
    Returns:
        起卦結果
    """
    print("="*70)
    print("【A3 問卷起卦】")
    print("="*70)
    
    # 收集問題
    if not question:
        print("\n請輸入您的問題：")
        print("（例如：該不該跳槽？這段感情該不該繼續？）")
        question = input("→ ").strip()
        if not question:
            question = "請指引方向"
    
    print(f"\n✓ 問題：{question}")
    
    # 分類問題
    q_type = classify_question(question)
    type_name = DEFAULT_ASPECTS.get(q_type, {}).get('name', '一般決策')
    print(f"✓ 問題類型：{type_name}")
    print("-"*70)
    
    # 取得評估面向
    aspects = get_aspects_for_question(question)
    
    # 顯示六個面向預覽
    print("\n將針對以下六個面向進行評估：")
    print("-"*70)
    for i, aspect in enumerate(aspects):
        yao_type = "內" if i < 3 else "外"
        print(f"  {i+1}. ({yao_type}) {aspect[:40]}...")
    print("-"*70)
    
    input("\n按 Enter 開始評分...")
    
    # 收集分數
    scores = _collect_scores_interactive(question, aspects)
    
    # 轉換成爻值
    yao_values = [score_to_yao(s) for s in scores]
    
    # 計算卦象
    hexagrams = compute_b_stage(yao_values)
    
    return {
        'method': 'A3',
        'method_name': '問卷起卦',
        'question': question,
        'question_type': q_type,
        'aspects': aspects,
        'scores': scores,
        'yao_values': yao_values,
        'yao_names': [get_yao_name(y) for y in yao_values],
        'hexagrams': hexagrams
    }


def quick_questionnaire(question: str, scores: List[int]) -> Dict:
    """
    快速問卷起卦（非互動式）
    
    Args:
        question: 問題
        scores: 六個分數 [0-10 × 6]
    
    Returns:
        起卦結果
    """
    if len(scores) != 6:
        raise ValueError("需要 6 個分數")
    
    if not all(0 <= s <= 10 for s in scores):
        raise ValueError("分數必須在 0-10 之間")
    
    return questionnaire_divination(question, scores=scores, interactive=False)
