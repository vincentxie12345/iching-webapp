"""
易力決策 - LLM 微調適配器
用於 A2 模式，將中性版文字根據問題進行微調
支援漸進式載入：s1 → s2 → s6（個別呼叫）
"""

import os
from anthropic import Anthropic


class ClaudeLLMAdapter:
    """Claude API 微調適配器"""
    
    def __init__(self, api_key=None, use_haiku=True):
        if api_key is None:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=api_key)
        
        # Haiku 快又便宜，適合改寫任務
        if use_haiku:
            self.model = "claude-3-5-haiku-20241022"
        else:
            self.model = "claude-sonnet-4-20250514"
    
    def adapt(self, content, question, section_name):
        """
        將中性版內容根據問題微調
        
        Args:
            content: 中性版文字
            question: 用戶問題
            section_name: 段落名稱（用於 prompt 調整）
        
        Returns:
            微調後的文字
        """
        prompt = f"""你是一位專業的易經解讀助手。

用戶的問題是：「{question}」

以下是一段中性的解卦描述，請根據用戶的問題，將描述中的抽象概念具體化，讓用戶能更容易理解這段話與他的問題的關聯。

原文：
{content}

要求：
1. 保持原文的核心意涵和結構
2. 將「你」的處境自然連結到用戶的問題情境
3. 可適當加入與問題相關的具體比喻或情境
4. 字數控制在原文的 1.0-1.3 倍之間
5. 語氣保持溫和、鼓勵、中性
6. 直接輸出修改後的文字，不要加任何前綴說明

修改後："""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"LLM 微調失敗（{section_name}）：{e}")
            return content  # 失敗時返回原文
    
    def adapt_single(self, content, question, section_name):
        """單獨微調一個段落（用於漸進式載入）"""
        return self.adapt(content, question, section_name)


class OllamaLLMAdapter:
    """Ollama 本地 LLM 適配器（預留）"""
    
    def __init__(self, model_name="llama3.2:1b"):
        self.model_name = model_name
    
    def adapt(self, content, question, section_name):
        return content
