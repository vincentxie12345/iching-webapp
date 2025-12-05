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
            data_path = os.path.dirname(os.path.abspath(__file__))
        
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
    
    # === 評分系統 ===
    def _score_hex(self, hex_obj):
        """評估單個卦象的品質 (0-1)"""
        labels = hex_obj.get('modern2', {}).get('labels', {})
        
        strength_map = {"弱": 0.3, "略弱": 0.4, "中等": 0.6, "略強": 0.7, "強": 0.9}
        alignment_map = {"低度吻合": 0.3, "部分吻合": 0.5, "中度吻合": 0.6, "高度吻合": 0.9}
        flow_map = {"阻滯較多": 0.3, "阻滯": 0.4, "大致持平": 0.6, "順暢": 0.8, "流暢": 0.9}
        
        s = strength_map.get(labels.get('strength', '中等'), 0.6)
        a = alignment_map.get(labels.get('alignment', '中度吻合'), 0.6)
        f = flow_map.get(labels.get('flow', '大致持平'), 0.6)
        
        return (s + a + f) / 3
    
    def _score_path(self, hex_target, hex_transition):
        """評估路徑品質：之卦 70% + 轉移卦 30%"""
        target_score = self._score_hex(hex_target)
        transition_score = self._score_hex(hex_transition)
        return target_score * 0.7 + transition_score * 0.3
    
    def _get_best_advice_positions(self, yao_values):
        """
        根據變爻情況，選出最佳建議的爻位
        
        邏輯：
        1. 單變爻：比較本卦 vs 之卦，決定是否促成
        2. 多變爻：排列組合找最佳之卦組合
        3. 無變爻：找最佳的 1-2 個爻位建議改變
        
        Returns:
            list of dict: [{'position': int, 'action': 'promote'/'prevent'/'change', 'score': float}]
        """
        from itertools import combinations
        
        ben_code = ''.join(['1' if v in [7, 9] else '0' for v in yao_values])
        ben_hex = self._get_entry_by_code(ben_code)
        ben_score = self._score_hex(ben_hex)
        
        change_positions = [i+1 for i, v in enumerate(yao_values) if v in [6, 9]]
        
        # === 情況 1：無變爻（靜卦）===
        if len(change_positions) == 0:
            # 嘗試每個位置變化，找最佳的 1-2 個
            candidates = []
            for pos in range(1, 7):
                # 模擬這個位置變化
                test_code = self._flip_bit(ben_code, pos)
                test_hex = self._get_entry_by_code(test_code)
                
                # 轉移卦：只有這一個位置是 1
                trans_bits = ['0'] * 6
                trans_bits[pos - 1] = '1'
                trans_code = ''.join(trans_bits)
                trans_hex = self._get_entry_by_code(trans_code)
                
                path_score = self._score_path(test_hex, trans_hex)
                
                candidates.append({
                    'position': pos,
                    'action': 'change',  # 建議主動改變
                    'score': path_score,
                    'zhi_code': test_code,
                    'improvement': path_score - ben_score
                })
            
            # 按分數排序，選最佳的
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            # 只選有正向改善的
            best = [c for c in candidates if c['improvement'] > 0][:2]
            
            # 如果第一名明顯領先，只返回一個
            if len(best) >= 2 and best[0]['score'] - best[1]['score'] > 0.1:
                return [best[0]]
            
            return best if best else [candidates[0]]  # 至少返回一個
        
        # === 情況 2：單變爻 ===
        if len(change_positions) == 1:
            pos = change_positions[0]
            
            # 計算之卦（變爻發生後）
            zhi_code = self._flip_bit(ben_code, pos)
            zhi_hex = self._get_entry_by_code(zhi_code)
            
            # 轉移卦
            trans_bits = ['0'] * 6
            trans_bits[pos - 1] = '1'
            trans_code = ''.join(trans_bits)
            trans_hex = self._get_entry_by_code(trans_code)
            
            zhi_score = self._score_path(zhi_hex, trans_hex)
            
            # 比較本卦 vs 之卦
            if zhi_score > ben_score:
                # 之卦較好，順勢而為
                return [{
                    'position': pos,
                    'action': 'promote',  # 9 順勢，6 也順勢
                    'score': zhi_score,
                    'improvement': zhi_score - ben_score
                }]
            else:
                # 之卦較差，守住不變
                return [{
                    'position': pos,
                    'action': 'prevent',  # 阻止變化
                    'score': ben_score,
                    'improvement': 0
                }]
        
        # === 情況 3：多變爻 ===
        # 嘗試所有組合（2^n - 1 種，排除全不變）
        n = len(change_positions)
        candidates = []
        
        # 生成所有可能的子集（從 1 到 n 個變爻，排除 0 個即全不變）
        for r in range(1, n + 1):  # 從 1 開始，排除全不變
            for combo in combinations(change_positions, r):
                # combo 是要讓其發生變化的爻位
                test_code = ben_code
                for pos in combo:
                    test_code = self._flip_bit(test_code, pos)
                
                test_hex = self._get_entry_by_code(test_code)
                
                # 轉移卦：combo 中的位置是 1
                trans_bits = ['0'] * 6
                for pos in combo:
                    trans_bits[pos - 1] = '1'
                trans_code = ''.join(trans_bits)
                trans_hex = self._get_entry_by_code(trans_code)
                
                if trans_hex is None:  # 全 0 的情況
                    path_score = self._score_hex(test_hex)
                else:
                    path_score = self._score_path(test_hex, trans_hex)
                
                candidates.append({
                    'combo': combo,
                    'promote_positions': list(combo),
                    'prevent_positions': [p for p in change_positions if p not in combo],
                    'score': path_score,
                    'zhi_code': test_code
                })
        
        # 找最佳組合
        candidates.sort(key=lambda x: x['score'], reverse=True)
        best = candidates[0]
        
        # 轉換為建議格式
        result = []
        for pos in best['promote_positions']:
            result.append({
                'position': pos,
                'action': 'promote',
                'score': best['score']
            })
        for pos in best['prevent_positions']:
            result.append({
                'position': pos,
                'action': 'prevent',
                'score': best['score']
            })
        
        # 按位置排序
        result.sort(key=lambda x: x['position'])
        
        return result
    
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
        
        # 【5. 建議】- 使用最佳組合選擇
        best_positions = self._get_best_advice_positions(yao_values)
        advices = []
        
        for item in best_positions:
            pos = item['position']
            action = item['action']
            v = yao_values[pos - 1]
            scope = '內' if pos <= 3 else '外'
            
            # 根據 action 調整建議文字
            base_advice = ben_template.get('6789建議', {}).get(str(pos), {}).get(str(v), '')
            
            if action == 'promote':
                action_hint = '這是值得積極推動的方向，順勢而為會有好結果。' if scope == '內' else '外在條件支持這個變化，把握機會順勢推進。'
            elif action == 'prevent':
                action_hint = '這個變化目前不宜強推，守住現狀較為有利。' if scope == '內' else '外在變化暫時不利，建議觀望等待更好時機。'
            else:  # change（靜卦時建議主動改變）
                action_hint = '雖然目前穩定，但主動在此方向努力會帶來正向改變。' if scope == '內' else '可以主動觀察並創造這個方向的外在機會。'
            
            advices.append({
                'position': pos,
                'name': self.LINE_NAMES[pos],
                'advice': base_advice,
                'scope': scope,
                'action': action,
                'action_hint': action_hint
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
    
    # === 統一生成方法 ===
    def generate(self, yao_values, question=None, llm_adapter=None):
        """
        統一生成六點解卦
        
        Args:
            yao_values: list of 6 values
            question: 用戶問題（可選）
                - None: 返回中性版（A1 模式）
                - str: 有問題版（A2/A3 模式）
            llm_adapter: LLM 微調適配器（可選）
                - None: 返回中性版（即使有 question）
                - 有值: 微調 s1, s2, s6（關鍵段落）
        
        Returns:
            dict with meta and sections
        """
        # 先取得中性版（A1）
        result = self.generate_a1(yao_values)
        
        # 如果沒有 question，直接返回中性版
        if question is None:
            return result
        
        # 有 question，設定模式
        result['meta']['mode'] = 'A2'
        result['meta']['question'] = question
        
        # 如果沒有 adapter，返回中性版（只加 question 標記）
        if llm_adapter is None:
            return result
        
        # 有 adapter，只微調關鍵段落：s1, s2, s6
        # s3（變化過程）、s4（六階段）、s5（建議）保持中性版
        sections = result['sections']
        
        # 微調 s1 現況
        sections['s1_status']['content'] = llm_adapter.adapt(
            sections['s1_status']['content'], question, '現況'
        )
        
        # 微調 s2 變化趨勢
        sections['s2_trend']['content'] = llm_adapter.adapt(
            sections['s2_trend']['content'], question, '變化趨勢'
        )
        
        # 微調 s6 展望
        sections['s6_outlook']['content'] = llm_adapter.adapt(
            sections['s6_outlook']['content'], question, '展望'
        )
        
        return result
    
    # === A2 有問題版生成（保留向下相容）===
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
