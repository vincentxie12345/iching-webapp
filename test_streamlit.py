import os
from dotenv import load_dotenv
load_dotenv("/Users/vincenthsieh/pyprogram/.env", override=True)

import streamlit as st
st.set_page_config(page_title="API 測試")

st.title("API Key 測試")

# 顯示環境變數狀態
gemini_key = os.getenv('GEMINI_API_KEY', '')
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')

st.write(f"GEMINI_API_KEY: {'已設定 (' + gemini_key[:10] + '...)' if gemini_key else '未設定'}")
st.write(f"ANTHROPIC_API_KEY: {'已設定 (' + anthropic_key[:10] + '...)' if anthropic_key else '未設定'}")

if st.button("測試 Gemini"):
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("說 Hello")
        st.success(f"✅ Gemini: {response.text}")
    except Exception as e:
        st.error(f"❌ Gemini 錯誤: {e}")

if st.button("測試 Claude"):
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "說 Hello"}]
        )
        st.success(f"✅ Claude: {response.content[0].text}")
    except Exception as e:
        st.error(f"❌ Claude 錯誤: {e}")
