"""
易力決策 - 六點解卦生成模組
YiliGenerator: 生成六點解卦內容（純資料，不含渲染）

使用方式:
    generator = YiliGenerator()
    result = generator.generate_a1(yao_values)  # A1 制式答案
    result = generator.generate_a2(yao_values, question, llm_adapter)  # A2 有問題版
"""

import json
import os


class YiliGenerator:
    """生成六點解卦內容（純資料，不含渲染）"""
    
    def __init__(self, data_path=None):
        """載入三個 JSON"""
        if data_path is None:
            # 預設指向 data/ 目錄（從 core/ 往上一層再進 data/）
            data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        
        with open(os.path.join(data_path, 'i_ching_modern2.json'), 'r', encoding='utf-8') as f:
            self.modern2 = json.load(f)
        
        with open(os.path.join(data_path, 'yili_general.json'), 'r', encoding='utf-8') as f:
            self.general = json.load(f)
        
        with open(os.path.join(data_path, 'yili_4096_trends.json'), 'r', encoding='utf-8') as f:
            self.trends = json.load(f)
        
        # 常數
        self.LINE_NAMES = {
            1: "基礎能力", 2: "外在表現", 3: "成長潛力",
            4: "環境基本面", 5: "環境現況", 6: "環境趨勢"
        }
        self.STAGE_NAMES = ["根基", "表現", "潛力", "環境條件", "環境現況", "環境趨勢"]
        self.SCOPE_LABELS = ["內在", "內在", "內在", "外在", "外在", "外在"]
    
    # === 基礎計算 ===
    def _flip_bit(self, code, pos):
        """翻轉指定位置的爻"""
        bits = list(code)
        bits[pos - 1] = '0' if bits[pos - 1] == '1' else '1'
        return ''.join(bits)
    
    def _get_entry_by_code(self, code):
        """根據卦碼取得卦資料"""
        for entry in self.modern2.values():
            if entry['code'] == code:
                return entry
        return None
    
    def _get_hex_number_by_code(self, code):
        """根據卦碼取得卦號"""
        for k, entry in self.modern2.items():
            if entry['code'] == code:
                return k
        return None
    
    def calculate_hexagrams(self, yao_values):
        """
        從六爻值計算本卦、之卦、轉移卦
        
        Args:
            yao_values: list of 6 values, each is 6/7/8/9
        
        Returns:
            dict with ben, zhi, trans hexagram info
        """
        # 本卦：7,9 為陽(1)，6,8 為陰(0)
        ben_code = ''.join(['1' if v in [7, 9] else '0' for v in yao_values])
        ben_hex = self._get_entry_by_code(ben_code)
        ben_num = self._get_hex_number_by_code(ben_code)
        
        # 變爻位置：6,9 為變爻
        change_positions = [i+1 for i, v in enumerate(yao_values) if v in [6, 9]]
        
        # 之卦：變爻翻轉
        zhi_code = ben_code
        for pos in change_positions:
            zhi_code = self._flip_bit(zhi_code, pos)
        zhi_hex = self._get_entry_by_code(zhi_code)
        zhi_num = self._get_hex_number_by_code(zhi_code)
        
        # 轉移卦：變爻位置為1，其他為0
        trans_code = ''.join(['1' if v in [6, 9] else '0' for v in yao_values])
        trans_hex = self._get_entry_by_code(trans_code)
        trans_num = self._get_hex_number_by_code(trans_code)
        
        return {
            'yao_values': yao_values,
            'change_positions': change_positions,
            'ben': {'hex': ben_hex, 'num': ben_num, 'code': ben_code},
            'zhi': {'hex': zhi_hex, 'num': zhi_num, 'code': zhi_code},
            'trans': {'hex': trans_hex, 'num': trans_num, 'code': trans_code}
        }
    
    # === 文字處理 ===
    def _adapt_text_for_section(self, text, section_type):
        """根據段落類型調整文字"""
        if section_type == 'trans':  # 變化過程
            text = text.replace("你現在", "在變動的過程中，你")
            text = text.replace("你目前", "在這個階段，你")
        elif section_type == 'outlook':  # 展望
            text = text.replace("你現在", "屆時你")
            text = text.replace("你目前", "屆時你")
        return text
    
    # === A1 制式答案生成 ===
    def generate_a1(self, yao_values):
        """
        A1 制式答案：六點解卦（無 question）
        
        Args:
            yao_values: list of 6 values, each is 6/7/8/9
        
        Returns:
            dict with meta and sections
        """
        calc = self.calculate_hexagrams(yao_values)
        
        ben_num = calc['ben']['num']
        zhi_num = calc['zhi']['num']
        trans_num = calc['trans']['num']
        change_positions = calc['change_positions']
        
        ben_template = self.general.get(ben_num, {})
        zhi_template = self.general.get(zhi_num, {})
        trans_template = self.general.get(trans_num, {})
        
        trend_key = f"{ben_num}_{zhi_num}"
        trend_data = self.trends.get(trend_key, {})
        
        # 組裝結果
        result = {
            'meta': {
                'mode': 'A1',
                'question': None,
                'yao_values': yao_values,
                'ben_name': calc['ben']['hex']['name'],
                'ben_code': calc['ben']['code'],
                'zhi_name': calc['zhi']['hex']['name'],
                'zhi_code': calc['zhi']['code'],
                'trans_name': calc['trans']['hex']['name'] if calc['trans']['hex'] else None,
                'trans_code': calc['trans']['code'],
                'change_positions': change_positions,
                'is_static': len(change_positions) == 0
            },
            'sections': {}
        }
        
        # 【1. 現況】
        result['sections']['s1_status'] = {
            'title': '現況',
            'content': ben_template.get('卦解', '')
        }
        
        # 【2. 變化趨勢】
        result['sections']['s2_trend'] = {
            'title': '變化趨勢',
            'content': trend_data.get('趨勢', '')
        }
        
        # 【3. 變化過程】
        if len(change_positions) > 0:
            trans_text = trans_template.get('卦解', '')
            trans_text = self._adapt_text_for_section(trans_text, 'trans')
            result['sections']['s3_process'] = {
                'title': '變化過程中會面臨的情況',
                'content': trans_text
            }
        else:
            result['sections']['s3_process'] = None
        
        # 【4. 六階段】
        stages = []
        for i in range(1, 7):
            stages.append({
                'position': i,
                'scope': self.SCOPE_LABELS[i-1],
                'name': self.STAGE_NAMES[i-1],
                'content': ben_template.get('六階段', {}).get(str(i), ''),
                'is_change': i in change_positions
            })
        result['sections']['s4_stages'] = {
            'title': '六階段境遇',
            'stages': stages
        }
        
        # 【5. 建議】
        advices = []
        if len(change_positions) == 0:
            # 靜卦：六項都給建議
            for i in range(1, 7):
                v = yao_values[i-1]
                advices.append({
                    'position': i,
                    'name': self.LINE_NAMES[i],
                    'advice': ben_template.get('6789建議', {}).get(str(i), {}).get(str(v), ''),
                    'scope': '內' if i <= 3 else '外',
                    'action_hint': '這是你可以主動努力的方向。' if i <= 3 else '這需要觀察外在變化，抓住機會。'
                })
        else:
            # 變卦：只給變爻建議
            for pos in change_positions:
                v = yao_values[pos - 1]
                scope = '內' if pos <= 3 else '外'
                advices.append({
                    'position': pos,
                    'name': self.LINE_NAMES[pos],
                    'advice': ben_template.get('6789建議', {}).get(str(pos), {}).get(str(v), ''),
                    'scope': scope,
                    'action_hint': '這是你可以主動努力的方向。' if scope == '內' else '這需要觀察外在變化，抓住機會。'
                })
        
        result['sections']['s5_advice'] = {
            'title': '建議',
            'is_static': len(change_positions) == 0,
            'items': advices
        }
        
        # 【6. 展望】
        zhi_text = zhi_template.get('卦解', '')
        zhi_text = self._adapt_text_for_section(zhi_text, 'outlook')
        result['sections']['s6_outlook'] = {
            'title': '依建議行動後的展望',
            'content': zhi_text
        }
        
        return result
    
    # === A2 有問題版生成 ===
    def generate_a2(self, yao_values, question, llm_adapter=None):
        """
        A2 有問題版：中性版 + LLM 微調
        
        Args:
            yao_values: list of 6 values
            question: 用戶問題字串
            llm_adapter: LLM 微調適配器（需有 adapt 方法）
        
        Returns:
            dict with meta and sections (微調後)
        """
        # 先取得 A1 結果
        base_result = self.generate_a1(yao_values)
        base_result['meta']['mode'] = 'A2'
        base_result['meta']['question'] = question
        
        if llm_adapter is None:
            # 無 LLM，直接返回中性版
            return base_result
        
        # 有 LLM，進行微調
        sections = base_result['sections']
        
        # 微調各段落
        sections['s1_status']['content'] = llm_adapter.adapt(
            sections['s1_status']['content'], question, '現況'
        )
        sections['s2_trend']['content'] = llm_adapter.adapt(
            sections['s2_trend']['content'], question, '變化趨勢'
        )
        if sections['s3_process']:
            sections['s3_process']['content'] = llm_adapter.adapt(
                sections['s3_process']['content'], question, '變化過程'
            )
        
        # 微調六階段
        for stage in sections['s4_stages']['stages']:
            stage['content'] = llm_adapter.adapt(
                stage['content'], question, f"第{stage['position']}階段"
            )
        
        # 微調建議
        for item in sections['s5_advice']['items']:
            item['advice'] = llm_adapter.adapt(
                item['advice'], question, f"建議-{item['name']}"
            )
        
        # 微調展望
        sections['s6_outlook']['content'] = llm_adapter.adapt(
            sections['s6_outlook']['content'], question, '展望'
        )
        
        return base_result
    
    # === A3/A4 預留接口 ===
    def generate_a3(self, yao_values, question, questionnaire_data, llm_adapter=None):
        """A3 問卷版（預留）"""
        result = self.generate_a2(yao_values, question, llm_adapter)
        result['meta']['mode'] = 'A3'
        result['meta']['questionnaire'] = questionnaire_data
        return result
    
    def generate_a4(self, yao_values, question, agent_context, llm_adapter=None):
        """A4 Agent 版（預留）"""
        result = self.generate_a2(yao_values, question, llm_adapter)
        result['meta']['mode'] = 'A4'
        result['meta']['agent_context'] = agent_context
        return result
