# 載入環境變數（支援本地和雲端）
import os
from dotenv import load_dotenv

# 本地開發時讀取 .env
load_dotenv("/Users/vincenthsieh/pyprogram/.env", override=True)

# import streamlit
import streamlit as st

# 雲端部署時讀取 Streamlit secrets（用 try-except 避免本地報錯）
try:
    if 'ANTHROPIC_API_KEY' in st.secrets:
        os.environ['ANTHROPIC_API_KEY'] = st.secrets['ANTHROPIC_API_KEY']
    if 'GEMINI_API_KEY' in st.secrets:
        os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
except:
    pass  # 本地沒有 secrets.toml 時忽略

# 設定頁面（必須是第一個 Streamlit 指令）
st.set_page_config(
    page_title="易力決策",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 其他 import
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iching_system.core.dayan import dayan_six_yao, score_to_yao, get_yao_name
from iching_system.core.calculator import compute_b_stage
from iching_system.core.yili_generator import YiliGenerator
from iching_system.core.yili_llm_adapter import ClaudeLLMAdapter
from iching_system.divination.a3_questionnaire import get_aspects_for_question, classify_question

# 初始化 Generator 和 Adapter（只載入一次）
@st.cache_resource
def get_generator():
    return YiliGenerator()

@st.cache_resource
def get_adapter():
    return ClaudeLLMAdapter()

# 樣式 + PWA 設定
st.markdown("""
<style>
    .stButton > button { width: 100%; height: 3em; font-size: 1.2em; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
<link rel="manifest" href="static/manifest.json">
<link rel="apple-touch-icon" href="static/icon-192.png">
<meta name="theme-color" content="#6c5ce7">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="易力決策">
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 style="text-align:center">🔮 易力決策</h1>', unsafe_allow_html=True)
    
    if 'step' not in st.session_state:
        st.session_state.step = 'select_method'
    if 'method' not in st.session_state:
        st.session_state.method = None
    if 'question' not in st.session_state:
        st.session_state.question = ''
    if 'scores' not in st.session_state:
        st.session_state.scores = [5, 5, 5, 5, 5, 5]
    
    if st.session_state.step == 'select_method':
        show_method_selection()
    elif st.session_state.step == 'input_question':
        show_question_input()
    elif st.session_state.step == 'a3_questionnaire':
        show_a3_questionnaire()
    elif st.session_state.step == 'divining':
        show_divining()
    elif st.session_state.step == 'result':
        show_result()

def show_method_selection():
    st.markdown("### 選擇起卦方式")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🙏 A1 默禱"):
            st.session_state.method = 'A1'
            st.session_state.question = ''
            st.session_state.step = 'divining'
            st.rerun()
        if st.button("📝 A3 問卷"):
            st.session_state.method = 'A3'
            st.session_state.step = 'input_question'
            st.rerun()
    with col2:
        if st.button("💭 A2 提問"):
            st.session_state.method = 'A2'
            st.session_state.step = 'input_question'
            st.rerun()
        if st.button("🤖 A4 Agent", disabled=True):
            pass
    
    with st.expander("📖 說明"):
        st.markdown("""
        **A1 默禱**：心中默想問題，系統隨機起卦，使用預生成的中性解卦
        
        **A2 提問**：輸入問題，系統隨機起卦，AI 根據問題微調解卦
        
        **A3 問卷**：回答六個評估問題，根據回答起卦
        """)

def show_question_input():
    method_name = 'A2 提問' if st.session_state.method == 'A2' else 'A3 問卷'
    st.markdown(f"### {method_name}")
    question = st.text_input("請輸入您的問題", placeholder="例如：該不該跳槽？")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 返回"):
            st.session_state.step = 'select_method'
            st.rerun()
    with col2:
        if st.button("➡️ 下一步"):
            if question.strip():
                st.session_state.question = question.strip()
                if st.session_state.method == 'A2':
                    st.session_state.step = 'divining'
                else:
                    st.session_state.step = 'a3_questionnaire'
                st.rerun()
            else:
                st.warning("請輸入問題")

def show_a3_questionnaire():
    st.markdown("### A3 問卷起卦")
    st.markdown(f"**問題**：{st.session_state.question}")
    st.markdown("---")
    
    aspects = get_aspects_for_question(st.session_state.question)
    st.markdown("請為以下六個面向評分（0=非常弱，10=非常強）：")
    
    scores = []
    for i, aspect in enumerate(aspects):
        yao_type = "內" if i < 3 else "外"
        score = st.slider(f"**{i+1}. ({yao_type})** {aspect}", 0, 10, st.session_state.scores[i], key=f"score_{i}")
        scores.append(score)
    
    st.session_state.scores = scores
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 返回"):
            st.session_state.step = 'input_question'
            st.rerun()
    with col2:
        if st.button("🎴 開始占卜"):
            st.session_state.step = 'divining'
            st.rerun()

def show_divining():
    st.markdown("### 🔮 占卜中...")
    method = st.session_state.method
    question = st.session_state.question
    
    with st.spinner("正在起卦..."):
        try:
            if method == 'A1':
                yao_values = dayan_six_yao()
                display_question = "（默禱，題目在心中）"
            elif method == 'A2':
                yao_values = dayan_six_yao()
                display_question = question
            elif method == 'A3':
                yao_values = [score_to_yao(s) for s in st.session_state.scores]
                display_question = question
            else:
                st.error(f"未知方式：{method}")
                return
            
            st.session_state.yao_values = yao_values
            st.session_state.display_question = display_question
        except Exception as e:
            st.error(f"起卦失敗：{e}")
            return
    
    # 先生成預生成版本（秒出）
    generator = get_generator()
    result = generator.generate_a1(yao_values)
    result['meta']['question'] = question if method != 'A1' else ''
    
    st.session_state.result = result
    st.session_state.method_used = method
    
    # 初始化微調狀態
    st.session_state.adapted = {'s1': False, 's2': False, 's6': False}
    st.session_state.step = 'result'
    st.rerun()


def show_result():
    st.markdown("### 🔮 占卜結果")
    st.markdown(f"**問題**：{st.session_state.display_question}")
    
    result = st.session_state.result
    meta = result['meta']
    sections = result['sections']
    method = st.session_state.get('method_used', 'A1')
    question = st.session_state.get('display_question', '')
    
    # A2/A3 模式：漸進式微調
    need_adapt = method in ['A2', 'A3'] and question and question != "（默禱，題目在心中）"
    adapted = st.session_state.get('adapted', {'s1': False, 's2': False, 's6': False})
    
    # 卦象資訊
    with st.expander("📊 卦象資訊"):
        col1, col2 = st.columns(2)
        col1.metric("本卦", f"（{meta['ben_code']}）")
        col2.metric("之卦", f"（{meta['zhi_code']}）" if not meta['is_static'] else "無變爻")
        if not meta['is_static']:
            st.text(f"變爻位置：{meta['change_positions']}")
        st.text(f"六爻：{st.session_state.yao_values}")
    
    st.markdown("---")
    
    # 1. 現況 - 進入頁面就微調
    s1 = sections['s1_status']
    if need_adapt and not adapted['s1']:
        with st.spinner("AI 正在解讀現況..."):
            adapter = get_adapter()
            s1['content'] = adapter.adapt_single(s1['content'], question, 's1')
            adapted['s1'] = True
            st.session_state.adapted = adapted
    
    with st.expander(f"📍 1. {s1['title']}（{meta['ben_code']}）", expanded=True):
        st.markdown(s1['content'])
    
    # 2. 變化趨勢 - 點開時微調
    s2 = sections['s2_trend']
    s2_expander = st.expander(f"📈 2. {s2['title']}（{meta['ben_code']}）→（{meta['zhi_code']}）")
    with s2_expander:
        if need_adapt and not adapted['s2']:
            with st.spinner("AI 正在分析趨勢..."):
                adapter = get_adapter()
                s2['content'] = adapter.adapt_single(s2['content'], question, 's2')
                adapted['s2'] = True
                st.session_state.adapted = adapted
        st.markdown(s2['content'])
    
    # 3. 變化過程（預生成，秒出）
    s3 = sections['s3_process']
    if s3:
        with st.expander(f"🔄 3. {s3['title']}（{meta['trans_code']}）"):
            st.markdown(s3['content'])
    
    # 4. 六階段（預生成，秒出）
    s4 = sections['s4_stages']
    with st.expander(f"📅 4. {s4['title']}"):
        for stage in s4['stages']:
            marker = "⚡ " if stage['is_change'] else ""
            st.markdown(f"**{marker}第{stage['position']}階段（{stage['scope']}・{stage['name']}）**")
            st.markdown(stage['content'])
            st.markdown("---")
    
    # 5. 建議（預生成，秒出，跟 s3, s4 一樣）
    s5 = sections['s5_advice']
    with st.expander(f"💡 5. {s5['title']}"):
        if s5['is_static']:
            st.markdown("目前沒有明顯的變動跡象，六個面向的建議如下：")
        else:
            st.markdown("核心考量在於把握以下方向：")
        st.markdown("")
        for item in s5['items']:
            st.markdown(f"**第{item['position']}項：{item['name']}**")
            st.markdown(item['advice'])
            st.markdown(f"*→ {item['action_hint']}*")
            st.markdown("---")
    
    # 6. 展望 - 點開時微調（跟 s2 一樣）
    s6 = sections['s6_outlook']
    s6_expander = st.expander(f"🌟 6. {s6['title']}（{meta['zhi_code']}）")
    with s6_expander:
        if need_adapt and not adapted['s6']:
            with st.spinner("AI 正在分析未來展望..."):
                adapter = get_adapter()
                s6['content'] = adapter.adapt_single(s6['content'], question, 's6')
                adapted['s6'] = True
                st.session_state.adapted = adapted
        st.markdown("如果依照上述建議採取行動，未來的局面將會是：")
        st.markdown("")
        st.markdown(s6['content'])
    
    st.markdown("---")
    if st.button("🔄 重新占卜"):
        st.session_state.step = 'select_method'
        st.session_state.method = None
        st.session_state.question = ''
        st.session_state.scores = [5, 5, 5, 5, 5, 5]
        st.session_state.adapted = {'s1': False, 's2': False, 's6': False}
        st.rerun()


if __name__ == "__main__":
    main()
