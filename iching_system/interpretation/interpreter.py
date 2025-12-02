# iching_system/interpretation/interpreter.py
"""
統一解卦器 - 支援本地和雲端部署
"""

import os
import copy
from typing import Dict, Optional

# 載入環境變數（本地）
from dotenv import load_dotenv
load_dotenv("/Users/vincenthsieh/pyprogram/.env", override=True)

# 支援 Streamlit secrets（雲端）- 用 try-except 避免本地報錯
try:
    import streamlit as st
    if 'ANTHROPIC_API_KEY' in st.secrets:
        os.environ['ANTHROPIC_API_KEY'] = st.secrets['ANTHROPIC_API_KEY']
    if 'GEMINI_API_KEY' in st.secrets:
        os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
except:
    pass


# ============================================================================
# 編碼修復工具
# ============================================================================

def _fix_encoding(s: str) -> str:
    """修復雙重 UTF-8 編碼的字串"""
    if not isinstance(s, str):
        return str(s) if s is not None else ''
    if not s:
        return s
    try:
        fixed = s.encode('latin-1').decode('utf-8')
        return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    try:
        fixed = s.encode('cp1252').decode('utf-8')
        return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    try:
        fixed = s.encode('iso-8859-1').decode('utf-8')
        return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return s


def _fix_hex_data(hex_obj: Dict) -> Dict:
    """修復卦象資料中的編碼問題"""
    if not hex_obj:
        return {}
    result = copy.deepcopy(hex_obj)
    if 'name' in result:
        result['name'] = _fix_encoding(result['name'])
    if 'modern2' in result:
        m2 = result['modern2']
        if 'labels' in m2 and isinstance(m2['labels'], dict):
            for key in m2['labels']:
                if isinstance(m2['labels'][key], str):
                    m2['labels'][key] = _fix_encoding(m2['labels'][key])
        if 'neutral_explanation' in m2:
            m2['neutral_explanation'] = _fix_encoding(m2['neutral_explanation'])
        if 'lines' in m2 and isinstance(m2['lines'], list):
            for line in m2['lines']:
                if 'neutral_line' in line:
                    line['neutral_line'] = _fix_encoding(line['neutral_line'])
                if 'stage' in line:
                    line['stage'] = _fix_encoding(line['stage'])
                if 'action_hints' in line and isinstance(line['action_hints'], dict):
                    hints = line['action_hints']
                    for key in hints:
                        if isinstance(hints[key], str):
                            hints[key] = _fix_encoding(hints[key])
                        elif isinstance(hints[key], list):
                            hints[key] = [_fix_encoding(x) if isinstance(x, str) else x for x in hints[key]]
    return result


# ============================================================================
# LLM 工具
# ============================================================================

def _get_llm_client():
    """取得 LLM 客戶端"""
    # 優先使用 Claude（因為環境變數設定較穩定）
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        from anthropic import Anthropic
        return Anthropic(api_key=anthropic_key), 'claude'
    
    # 備用 Gemini
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if gemini_key:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        return genai.GenerativeModel('gemini-2.0-flash-exp'), 'gemini'
    
    return None, None


def _call_llm(prompt: str, max_tokens: int = 500) -> str:
    """調用 LLM"""
    client, provider = _get_llm_client()
    
    if not client:
        return "[需要設定 GEMINI_API_KEY 或 ANTHROPIC_API_KEY]"
    
    try:
        if provider == 'gemini':
            response = client.generate_content(prompt)
            return response.text.strip()
        else:  # claude
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    except Exception as e:
        return f"[LLM 錯誤: {str(e)[:50]}]"


# ============================================================================
# 從 modern2 取得資料的輔助函數
# ============================================================================

def _get_modern2_data(hex_obj: Dict) -> Dict:
    return hex_obj.get('modern2', {})

def _get_labels(hex_obj: Dict) -> Dict:
    m2 = _get_modern2_data(hex_obj)
    return m2.get('labels', {})

def _get_neutral_explanation(hex_obj: Dict) -> str:
    m2 = _get_modern2_data(hex_obj)
    return m2.get('neutral_explanation', '')

def _get_lines(hex_obj: Dict) -> list:
    m2 = _get_modern2_data(hex_obj)
    return m2.get('lines', [])

def _get_llm_seeds(hex_obj: Dict) -> Dict:
    m2 = _get_modern2_data(hex_obj)
    return m2.get('llm_seeds', {})


# ============================================================================
# 六點解卦函數
# ============================================================================

def generate_hex_summary(question: str, hex_obj: Dict, context: str = "現況") -> str:
    """生成卦象總結（第1點使用）"""
    hex_obj = _fix_hex_data(hex_obj)
    hex_name = hex_obj.get('name', '未知')
    hex_code = hex_obj.get('code', '000000')
    labels = _get_labels(hex_obj)
    neutral_exp = _get_neutral_explanation(hex_obj)
    
    prompt = f"""
請用繁體中文，根據以下卦象資料，解釋「{context}」的含義：

問題：{question}
卦名：{hex_name}
卦碼：{hex_code}

【卦象分析資料】：
- 強度：{labels.get('strength', '')}
- 步調：{labels.get('alignment', '')}
- 流向：{labels.get('flow', '')}
- 內外平衡：{labels.get('balance', '')}
- 中性解釋：{neutral_exp}

請用 3-4 句話說明這個卦象對問題的「{context}」解讀。
語氣平實，結合問題情境說明。
不要使用傳統易經術語。
直接輸出內容，不要有標題。
"""
    return _call_llm(prompt)


def generate_transition_summary(question: str, hex_from: Dict, hex_to: Dict) -> str:
    """生成變化趨勢說明（第2點）"""
    hex_from = _fix_hex_data(hex_from)
    hex_to = _fix_hex_data(hex_to)
    from_name = hex_from.get('name', '未知')
    to_name = hex_to.get('name', '未知')
    from_labels = _get_labels(hex_from)
    to_labels = _get_labels(hex_to)
    to_exp = _get_neutral_explanation(hex_to)
    
    prompt = f"""
請用繁體中文，說明從「{from_name}卦」到「{to_name}卦」的變化趨勢：

問題：{question}

【本卦 {from_name} 的特徵】：
- 強度：{from_labels.get('strength', '')}
- 流向：{from_labels.get('flow', '')}
- 平衡：{from_labels.get('balance', '')}

【之卦 {to_name} 的特徵】：
- 強度：{to_labels.get('strength', '')}
- 流向：{to_labels.get('flow', '')}
- 平衡：{to_labels.get('balance', '')}
- 解釋：{to_exp}

請用 3-4 句話說明「變化的趨勢」。
專注在「從A到B的變化方向」。
語氣平實，結合問題情境。
不要使用傳統易經術語。
直接輸出內容，不要有標題。
"""
    return _call_llm(prompt)


def generate_process_summary(question: str, hex_trans: Dict, hex_from: Dict, hex_to: Dict) -> str:
    """生成變化過程說明（第3點）"""
    hex_trans = _fix_hex_data(hex_trans)
    hex_from = _fix_hex_data(hex_from)
    hex_to = _fix_hex_data(hex_to)
    trans_name = hex_trans.get('name', '未知')
    from_name = hex_from.get('name', '未知')
    to_name = hex_to.get('name', '未知')
    trans_labels = _get_labels(hex_trans)
    trans_exp = _get_neutral_explanation(hex_trans)
    
    prompt = f"""
請用繁體中文，描述在變化過程中會面臨的情境：

問題：{question}

【變化趨勢】從「{from_name}」→「{to_name}」

【轉移卦】{trans_name}（代表過渡期的狀態）
- 強度：{trans_labels.get('strength', '')}
- 步調：{trans_labels.get('alignment', '')}
- 流向：{trans_labels.get('flow', '')}
- 中性解釋：{trans_exp}

請用 3-4 句話說明過渡期的情境。
語氣平實，結合問題情境說明。
不要使用傳統易經術語。
直接輸出內容，不要有標題。
"""
    return _call_llm(prompt)


def generate_six_lines(question: str, hex_trans: Dict, hex_from: Dict = None, hex_to: Dict = None, part3_content: str = "") -> str:
    """生成六爻境遇說明（第4點）"""
    hex_trans = _fix_hex_data(hex_trans)
    hex_from = _fix_hex_data(hex_from) if hex_from else {}
    hex_to = _fix_hex_data(hex_to) if hex_to else {}
    
    trans_name = hex_trans.get('name', '未知')
    from_name = hex_from.get('name', '未知') if hex_from else '未知'
    to_name = hex_to.get('name', '未知') if hex_to else '未知'
    
    lines = _get_lines(hex_trans)
    lines_info = ""
    for i, line in enumerate(lines):
        stage = _fix_encoding(line.get('stage', f'第{i+1}階段'))
        neutral_line = _fix_encoding(line.get('neutral_line', ''))
        lines_info += f"{i+1}. {stage}：{neutral_line}\n"
    
    prompt = f"""
請用繁體中文描述從本卦走向之卦的六個階段。

問題：{question}
本卦：{from_name}
之卦：{to_name}
轉移卦：{trans_name}

【六段素材】：
{lines_info}

請為每個階段寫 2-3 句描述，包含具體情境和感受。
格式：
(第一階段)：...
(第二階段)：...
...以此類推

不要使用傳統易經術語。
"""
    return _call_llm(prompt, max_tokens=2000)


def generate_advice(question: str, hex_now: Dict) -> str:
    """生成建議（第5點）"""
    hex_now = _fix_hex_data(hex_now)
    hex_name = hex_now.get('name', '未知')
    labels = _get_labels(hex_now)
    neutral_exp = _get_neutral_explanation(hex_now)
    
    prompt = f"""
請用繁體中文，針對問題給出具體建議：

問題：{question}
本卦：{hex_name}

【卦象分析】：
- 強度：{labels.get('strength', '')}
- 步調：{labels.get('alignment', '')}
- 流向：{labels.get('flow', '')}
- 解釋：{neutral_exp}

請用 3-4 句話給出具體建議。
語氣實用，避免空泛。
不要使用傳統易經術語。
直接輸出內容，不要有標題。
"""
    return _call_llm(prompt)


def generate_prospect(question: str, hex_target: Dict, advice_text: str) -> str:
    """生成展望（第6點）"""
    hex_target = _fix_hex_data(hex_target)
    hex_name = hex_target.get('name', '未知')
    labels = _get_labels(hex_target)
    neutral_exp = _get_neutral_explanation(hex_target)
    
    prompt = f"""
請用繁體中文，描述按照建議行動後的未來展望：

問題：{question}
之卦：{hex_name}

【第5點給出的建議】：
{advice_text}

【之卦資料】：
- 強度：{labels.get('strength', '')}
- 流向：{labels.get('flow', '')}
- 解釋：{neutral_exp}

請用 3-4 句話描述按照建議後的未來狀態。
語氣用「若能...」等條件句。
不要使用傳統易經術語。
直接輸出內容，不要有標題。
"""
    return _call_llm(prompt)


# ============================================================================
# 主函數
# ============================================================================

def interpret(question: str, hexagrams: Dict, show_original: bool = False, display: bool = True) -> Dict:
    """統一解卦（核心函數）"""
    hex_now = _fix_hex_data(hexagrams['本卦'])
    hex_target = _fix_hex_data(hexagrams['之卦'])
    hex_trans = _fix_hex_data(hexagrams['轉移卦'])
    
    now_code = hex_now.get('code', '??????')
    target_code = hex_target.get('code', '??????')
    trans_code = hex_trans.get('code', '??????')
    now_name = hex_now.get('name', '未知')
    target_name = hex_target.get('name', '未知')
    trans_name = hex_trans.get('name', '未知')
    
    result = {}
    
    # 1. 現況
    if display:
        print(f"\n【1. 現況】：{now_name}卦 ({now_code})")
    result['1_現況'] = generate_hex_summary(question, hex_now, "現況")
    if display:
        print(result['1_現況'])
    
    # 2. 變化趨勢
    if display:
        print(f"\n【2. 變化趨勢】：{now_name}→{target_name}")
    result['2_變化趨勢'] = generate_transition_summary(question, hex_now, hex_target)
    if display:
        print(result['2_變化趨勢'])
    
    # 3. 變化過程
    if display:
        print(f"\n【3. 變化過程】：{trans_name}卦")
    result['3_變化過程'] = generate_process_summary(question, hex_trans, hex_now, hex_target)
    if display:
        print(result['3_變化過程'])
    
    # 4. 六爻境遇
    if display:
        print(f"\n【4. 各階段境遇】")
    result['4_六爻境遇'] = generate_six_lines(question, hex_trans, hex_from=hex_now, hex_to=hex_target)
    if display:
        print(result['4_六爻境遇'])
    
    # 5. 建議
    if display:
        print("\n【5. 建議】")
    result['5_建議'] = generate_advice(question, hex_now)
    if display:
        print(result['5_建議'])
    
    # 6. 展望
    if display:
        print(f"\n【6. 展望】：{target_name}卦")
    result['6_展望'] = generate_prospect(question, hex_target, result['5_建議'])
    if display:
        print(result['6_展望'])
    
    return result


def quick_interpret(question: str, hexagrams: Dict) -> Dict:
    """快速解卦（不顯示過程）"""
    return interpret(question, hexagrams, display=False)
