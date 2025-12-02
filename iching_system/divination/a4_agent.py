# iching_system/divination/a4_agent.py
"""
A4 Agent 起卦
=============
結合問卷和 AI Agent 的混合起卦方式

A4-1（問自己）：
- 內三爻：問卷（主觀評估）
- 外三爻：AI Agent（客觀資料）

A4-2（問他者）：
- 六爻全部：AI Agent（客觀分析）
- 狀態：進階研究中

適合：需要結合主觀判斷和客觀資料的決策
"""

import os
import re
import json
import time
from typing import Dict, List, Optional
from ..core.dayan import score_to_yao, get_yao_name
from ..core.calculator import compute_b_stage


# API 延遲控制
_last_api_call = 0
_api_delay = 1  # 秒


# 問卷題目（與 A3 一致，根據問題類型選用）
QUESTION_ASPECTS = {
    "career": {
        "name": "職涯決策",
        "inner": [
            "關於這個決定的內在動機，是否因為真心想要改變而非逃避現狀",
            "關於個人現有的專業技能、工作經驗、人脈資源是否足以支撐這個決定",
            "關於這個決定後的學習成長空間、職涯發展潛力，以及可能面臨的風險"
        ],
        "outer": [
            "關於家人朋友的支持態度、新環境的文化氛圍和基本工作條件",
            "關於目前在相關領域的實際表現、他人評價和市場競爭力",
            "關於所處行業的未來發展趨勢、就業市場變化和經濟大環境走向"
        ]
    },
    "relationship": {
        "name": "感情決策",
        "inner": [
            "關於這段感情中的內心真實感受，是否出於真心想要經營",
            "關於自己在感情中的付出能力、溝通技巧和情緒管理成熟度",
            "關於這段關係的成長空間、長期發展潛力，以及可能的挑戰"
        ],
        "outer": [
            "關於雙方家庭的態度、朋友圈的看法和基本生活條件的匹配度",
            "關於目前感情的實際互動品質、雙方的投入程度和默契度",
            "關於社會環境對這段感情的影響、價值觀的變遷和長期相處趨勢"
        ]
    },
    "general": {
        "name": "一般決策",
        "inner": [
            "關於這個決定的內在動機和真實意願強度",
            "關於現有的資源、能力和準備程度",
            "關於這個決定的發展潛力和可能風險"
        ],
        "outer": [
            "關於周圍環境的支持程度和基本條件",
            "關於目前的實際狀況和外界反應",
            "關於大環境趨勢和長期發展前景"
        ]
    }
}


def _classify_question(question: str) -> str:
    """分類問題類型"""
    career_keywords = ['工作', '跳槽', '職業', '創業', '升遷', '加薪', '辭職', '轉職', '求職', '深造', '讀書']
    relationship_keywords = ['感情', '愛情', '結婚', '分手', '交往', '對象', '另一半', '男友', '女友', '婚姻']
    
    for kw in career_keywords:
        if kw in question:
            return 'career'
    
    for kw in relationship_keywords:
        if kw in question:
            return 'relationship'
    
    return 'general'


def _get_gemini_model():
    """取得 Gemini 模型"""
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        raise ValueError("未設定 GEMINI_API_KEY 環境變數")
    
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-3-pro-preview')


def _call_gemini(prompt: str, max_retries: int = 3) -> str:
    """
    調用 Gemini API（含延遲和重試機制）
    """
    global _last_api_call
    
    # 確保間隔足夠
    elapsed = time.time() - _last_api_call
    if elapsed < _api_delay:
        time.sleep(_api_delay - elapsed)
    
    model = _get_gemini_model()
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            _last_api_call = time.time()
            return response.text.strip()
        except Exception as e:
            if '429' in str(e) or 'quota' in str(e).lower():
                wait = 20 * (attempt + 1)
                print(f"    ⏳ API 限制，等待 {wait} 秒...")
                time.sleep(wait)
            else:
                raise e
    
    raise Exception("API 調用失敗")


def _extract_context_info(description: str) -> Dict:
    """
    從用戶描述中提取關鍵資訊
    """
    prompt = f"""
請從以下描述中提取關鍵資訊：

描述：{description}

請以 JSON 格式輸出：
{{
    "industry": "行業",
    "position": "職位",
    "skills": "技能",
    "concerns": "關注點",
    "keywords": ["關鍵字1", "關鍵字2"]
}}

只輸出 JSON，不要其他文字。
"""
    
    try:
        response = _call_gemini(prompt)
        
        # 清理 JSON
        json_text = re.sub(r'```json\s*', '', response)
        json_text = re.sub(r'```\s*', '', json_text)
        
        return json.loads(json_text)
    except:
        return {
            "industry": "",
            "position": "",
            "skills": "",
            "concerns": "",
            "keywords": []
        }


def _generate_market_info(query: str) -> str:
    """
    使用 Gemini 生成市場資訊
    """
    prompt = f"""
請提供關於「{query}」的最新資訊（2024-2025）。

請包含：
1. 市場趨勢或現況
2. 相關數據（如薪資範圍、成長率）
3. 工作環境或條件
4. 發展前景

以 3-5 句話簡短回答。
"""
    
    try:
        return _call_gemini(prompt)
    except:
        return ""


def _analyze_and_score(aspect: str, data: str, question: str) -> int:
    """
    分析資料並評分
    """
    if not data:
        return 5  # 無資料返回中性分數
    
    prompt = f"""
基於以下資訊評估「{aspect}」的狀況：

問題：{question}
資料：{data}

評分標準（0-10分）：
0-2分：非常不利
3-5分：偏不利
6-8分：偏有利
9-10分：非常有利

請只回答一個數字（0-10）：
"""
    
    try:
        response = _call_gemini(prompt)
        numbers = re.findall(r'\d+', response)
        if numbers:
            score = int(numbers[0])
            if 0 <= score <= 10:
                return score
        return 5
    except:
        return 5


def agent_divination_a4_1(
    question: str,
    description: Optional[str] = None,
    inner_scores: Optional[List[int]] = None,
    interactive: bool = True
) -> Dict:
    """
    A4-1 混合起卦（問自己）
    
    內三爻：問卷評分（主觀）
    外三爻：AI Agent 收集資料評分（客觀）
    
    Args:
        question: 問題
        description: 背景描述（可選，互動時會詢問）
        inner_scores: 內三爻預設分數（可選）
        interactive: 是否互動式
    
    Returns:
        起卦結果
    """
    print("="*70)
    print("【A4-1 混合式起卦】")
    print("="*70)
    print(f"問題：{question}")
    print("="*70)
    
    # 分類問題，取得對應的面向
    q_type = _classify_question(question)
    q_aspects = QUESTION_ASPECTS[q_type]
    inner_aspects = q_aspects['inner']
    outer_aspects = q_aspects['outer']
    
    # Step 0: 收集背景描述
    if not description and interactive:
        print("\n【Step 0: 背景資訊】")
        print("請描述您的情況（越詳細越好）：")
        description = input("→ ").strip()
    
    description = description or question
    
    # 把問題和背景加起來一起分析
    full_context = f"{question}\n{description}" if description != question else question
    
    # 提取關鍵資訊
    print("\n正在分析背景資訊...")
    context = _extract_context_info(full_context)
    print(f"✓ 已提取關鍵資訊")
    
    # Step 1: 內三爻（問卷）
    print("\n【Step 1: 內在評估（問卷）】")
    
    if inner_scores and len(inner_scores) == 3:
        scores_inner = inner_scores
    elif interactive:
        scores_inner = []
        for i, aspect in enumerate(inner_aspects):
            print(f"\n【第 {i+1} 題】{aspect}")
            print("（0=非常弱，10=非常強）")
            while True:
                try:
                    score = int(input("評分：").strip())
                    if 0 <= score <= 10:
                        break
                except:
                    print("請輸入 0-10")
            scores_inner.append(score)
            print(f"✓ {score} 分 → {get_yao_name(score_to_yao(score))}")
    else:
        scores_inner = [5, 5, 5]
    
    print(f"\n✓ 內三爻分數：{scores_inner}")
    
    # Step 2: 外三爻（AI Agent）
    print("\n【Step 2: 外部環境分析（AI Agent）】")
    
    keywords = context.get('keywords', [question[:10]])
    scores_outer = []
    
    for i, aspect in enumerate(outer_aspects):
        print(f"\n【第 {i+4} 題】{aspect}")
        print("  正在收集資料...")
        
        # 生成搜尋關鍵字
        query = f"{keywords[0] if keywords else question[:10]} {aspect[:10]}"
        
        # 收集資料
        data = _generate_market_info(query)
        
        if data:
            print(f"  ✓ 已收集資料")
        else:
            print(f"  ⚠ 無法收集資料，使用中性評分")
        
        # 評分
        score = _analyze_and_score(aspect, data, question)
        scores_outer.append(score)
        print(f"  ✓ {score} 分 → {get_yao_name(score_to_yao(score))}")
    
    print(f"\n✓ 外三爻分數：{scores_outer}")
    
    # 合併分數
    all_scores = scores_inner + scores_outer
    yao_values = [score_to_yao(s) for s in all_scores]
    
    # 計算卦象
    hexagrams = compute_b_stage(yao_values)
    
    print("\n" + "="*70)
    print("【A4-1 起卦完成】")
    print(f"六爻分數：{all_scores}")
    print(f"六爻數值：{yao_values}")
    print(f"本卦：{hexagrams['本卦']['name']}")
    print(f"之卦：{hexagrams['之卦']['name']}")
    print("="*70)
    
    return {
        'method': 'A4-1',
        'method_name': '混合式起卦',
        'question': question,
        'description': description,
        'context': context,
        'inner_scores': scores_inner,
        'outer_scores': scores_outer,
        'scores': all_scores,
        'yao_values': yao_values,
        'yao_names': [get_yao_name(y) for y in yao_values],
        'hexagrams': hexagrams
    }


def quick_agent_divination(question: str, description: str, inner_scores: List[int]) -> Dict:
    """
    快速 Agent 起卦（非互動式）
    
    Args:
        question: 問題
        description: 背景描述
        inner_scores: 內三爻分數 [0-10 × 3]
    """
    return agent_divination_a4_1(
        question=question,
        description=description,
        inner_scores=inner_scores,
        interactive=False
    )


# A4-2 進階研究版本（暫停）
def agent_divination_a4_2(question: str, subject: str, background: str) -> Dict:
    """
    A4-2 全 Agent 起卦（問他者）
    
    六爻全部由 AI Agent 評估
    
    狀態：進階研究中，基本架構可用
    """
    raise NotImplementedError("A4-2 尚在進階研究中")
