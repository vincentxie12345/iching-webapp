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
    page_title="易經占卜",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 其他 import
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iching_system.core.dayan import dayan_six_yao, score_to_yao, get_yao_name
from iching_system.core.calculator import compute_b_stage
from iching_system.divination.a3_questionnaire import get_aspects_for_question, classify_question
from iching_system.interpretation.interpreter import interpret

# 樣式
st.markdown("""
<style>
    .stButton > button { width: 100%; height: 3em; font-size: 1.2em; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 style="text-align:center">🔮 易經占卜</h1>', unsafe_allow_html=True)
    
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
        **A1 默禱**：心中默想問題，系統隨機起卦，解卦用「這件事」呈現
        
        **A2 提問**：輸入問題，系統隨機起卦，解卦針對問題回答
        
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
                interpret_question = "這件事"
            elif method == 'A2':
                yao_values = dayan_six_yao()
                display_question = question
                interpret_question = question
            elif method == 'A3':
                yao_values = [score_to_yao(s) for s in st.session_state.scores]
                display_question = question
                interpret_question = question
            else:
                st.error(f"未知方式：{method}")
                return
            
            hexagrams = compute_b_stage(yao_values)
            st.session_state.yao_values = yao_values
            st.session_state.hexagrams = hexagrams
            st.session_state.display_question = display_question
            st.session_state.interpret_question = interpret_question
        except Exception as e:
            st.error(f"起卦失敗：{e}")
            return
    
    with st.spinner("正在解卦...（約 30-60 秒）"):
        try:
            interpretation = interpret(interpret_question, hexagrams, display=False)
            st.session_state.interpretation = interpretation
            st.session_state.step = 'result'
            st.rerun()
        except Exception as e:
            st.error(f"解卦失敗：{e}")

def show_result():
    st.markdown("### 🔮 占卜結果")
    st.markdown(f"**問題**：{st.session_state.display_question}")
    
    hexagrams = st.session_state.hexagrams
    with st.expander("📊 卦象資訊"):
        col1, col2, col3 = st.columns(3)
        col1.metric("本卦", hexagrams['本卦'].get('name', '—'))
        col2.metric("之卦", hexagrams['之卦'].get('name', '—'))
        col3.metric("轉移卦", hexagrams['轉移卦'].get('name', '—'))
        st.text(f"六爻：{st.session_state.yao_values}")
    
    st.markdown("---")
    interpretation = st.session_state.interpretation
    
    sections = [
        ('1_現況', '1. 現況', '📍', True),
        ('2_變化趨勢', '2. 變化趨勢', '📈', False),
        ('3_變化過程', '3. 變化過程', '🔄', False),
        ('4_六爻境遇', '4. 各階段境遇', '📅', False),
        ('5_建議', '5. 建議', '💡', True),
        ('6_展望', '6. 展望', '🌟', False),
    ]
    
    for key, title, icon, expanded in sections:
        if key in interpretation:
            with st.expander(f"{icon} {title}", expanded=expanded):
                st.markdown(interpretation[key])
    
    st.markdown("---")
    if st.button("🔄 重新占卜"):
        st.session_state.step = 'select_method'
        st.session_state.method = None
        st.session_state.question = ''
        st.session_state.scores = [5, 5, 5, 5, 5, 5]
        st.rerun()

if __name__ == "__main__":
    main()
