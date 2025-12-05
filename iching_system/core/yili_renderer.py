"""
易力決策 - 渲染模組
YiliRenderer: 將六點解卦資料渲染成各種格式

支援格式:
    - TerminalRenderer: 終端機文字輸出
    - HTMLRenderer: HTML 網頁 / PWA
    - JSONRenderer: JSON API 回傳
    - MarkdownRenderer: Markdown 格式
"""

import json


class YiliRenderer:
    """渲染基類"""
    
    def render(self, result):
        """
        渲染六點解卦結果
        
        Args:
            result: YiliGenerator 生成的結果 dict
        
        Returns:
            渲染後的字串
        """
        raise NotImplementedError


class TerminalRenderer(YiliRenderer):
    """終端機渲染"""
    
    def __init__(self, width=60):
        self.width = width
    
    def render(self, result):
        lines = []
        meta = result['meta']
        sections = result['sections']
        
        # Header
        lines.append("═" * self.width)
        lines.append("易 力 決 策".center(self.width))
        lines.append("═" * self.width)
        lines.append("")
        
        # Meta（保留布林碼，移除卦名）
        if meta.get('question'):
            lines.append(f"問題：{meta['question']}")
            lines.append("")
        lines.append(f"起卦結果：{meta['yao_values']}")
        lines.append(f"本卦：（{meta['ben_code']}）")
        if not meta['is_static']:
            lines.append(f"之卦：（{meta['zhi_code']}）")
            lines.append(f"變爻：{meta['change_positions']}")
        else:
            lines.append("之卦：無變爻（靜卦）")
        lines.append("")
        
        # 1. 現況（顯示本卦碼）
        s1 = sections['s1_status']
        lines.append(f"【1. {s1['title']}】（{meta['ben_code']}）")
        lines.append("")
        lines.append(s1['content'])
        lines.append("")
        
        # 2. 變化趨勢（顯示 本卦碼 → 之卦碼）
        s2 = sections['s2_trend']
        lines.append(f"【2. {s2['title']}】（{meta['ben_code']}）→（{meta['zhi_code']}）")
        lines.append("")
        lines.append(s2['content'])
        lines.append("")
        
        # 3. 變化過程（顯示轉移卦碼）
        s3 = sections['s3_process']
        if s3:
            lines.append(f"【3. {s3['title']}】（{meta['trans_code']}）")
            lines.append("")
            lines.append(s3['content'])
            lines.append("")
        
        # 4. 六階段
        s4 = sections['s4_stages']
        lines.append(f"【4. {s4['title']}】")
        lines.append("")
        for stage in s4['stages']:
            marker = "⚡" if stage['is_change'] else ""
            lines.append(f"第{stage['position']}階段（{stage['scope']}・你的{stage['name']}）：{marker}")
            lines.append(stage['content'])
            lines.append("")
        
        # 5. 建議
        s5 = sections['s5_advice']
        lines.append(f"【5. {s5['title']}】")
        lines.append("")
        if s5['is_static']:
            lines.append("目前沒有明顯的變動跡象，六個面向的建議如下：")
        else:
            lines.append("核心考量在於把握以下方向：")
        lines.append("")
        for item in s5['items']:
            lines.append(f"【第{item['position']}項：{item['name']}】")
            lines.append(item['advice'])
            lines.append(f"→ {item['action_hint']}")
            lines.append("")
        
        # 6. 展望（顯示之卦碼）
        s6 = sections['s6_outlook']
        lines.append(f"【6. {s6['title']}】（{meta['zhi_code']}）")
        lines.append("")
        lines.append("如果依照上述建議採取行動，未來的局面將會是：")
        lines.append("")
        lines.append(s6['content'])
        lines.append("")
        lines.append("═" * self.width)
        
        return "\n".join(lines)


class HTMLRenderer(YiliRenderer):
    """HTML/Web 渲染（PWA 用）"""
    
    def render(self, result):
        meta = result['meta']
        sections = result['sections']
        
        html = []
        html.append('<div class="yili-result">')
        
        # Header（保留布林碼，移除卦名）
        html.append('<header class="yili-header">')
        html.append('<h1>易力決策</h1>')
        if meta.get('question'):
            html.append(f'<p class="question">問題：{meta["question"]}</p>')
        html.append('<div class="meta">')
        html.append(f'<span class="ben">本卦：（{meta["ben_code"]}）</span>')
        if not meta['is_static']:
            html.append(f'<span class="zhi">之卦：（{meta["zhi_code"]}）</span>')
            html.append(f'<span class="change">變爻：{meta["change_positions"]}</span>')
        html.append('</div>')
        html.append('</header>')
        
        # Sections
        html.append('<main class="yili-sections">')
        
        # 1. 現況
        s1 = sections['s1_status']
        html.append('<section class="section s1">')
        html.append(f'<h2>1. {s1["title"]} <span class="code">（{meta["ben_code"]}）</span></h2>')
        html.append(f'<p>{s1["content"]}</p>')
        html.append('</section>')
        
        # 2. 變化趨勢
        s2 = sections['s2_trend']
        html.append('<section class="section s2">')
        html.append(f'<h2>2. {s2["title"]} <span class="code">（{meta["ben_code"]}）→（{meta["zhi_code"]}）</span></h2>')
        html.append(f'<p>{s2["content"]}</p>')
        html.append('</section>')
        
        # 3. 變化過程
        s3 = sections['s3_process']
        if s3:
            html.append('<section class="section s3">')
            html.append(f'<h2>3. {s3["title"]} <span class="code">（{meta["trans_code"]}）</span></h2>')
            html.append(f'<p>{s3["content"]}</p>')
            html.append('</section>')
        
        # 4. 六階段
        s4 = sections['s4_stages']
        html.append('<section class="section s4">')
        html.append(f'<h2>4. {s4["title"]}</h2>')
        html.append('<div class="stages">')
        for stage in s4['stages']:
            change_class = "is-change" if stage['is_change'] else ""
            html.append(f'<div class="stage {change_class}">')
            marker = "⚡ " if stage['is_change'] else ""
            html.append(f'<h3>{marker}第{stage["position"]}階段（{stage["scope"]}・{stage["name"]}）</h3>')
            html.append(f'<p>{stage["content"]}</p>')
            html.append('</div>')
        html.append('</div>')
        html.append('</section>')
        
        # 5. 建議
        s5 = sections['s5_advice']
        html.append('<section class="section s5">')
        html.append(f'<h2>5. {s5["title"]}</h2>')
        if s5['is_static']:
            html.append('<p class="advice-intro">目前沒有明顯的變動跡象，六個面向的建議如下：</p>')
        else:
            html.append('<p class="advice-intro">核心考量在於把握以下方向：</p>')
        html.append('<div class="advices">')
        for item in s5['items']:
            html.append('<div class="advice-item">')
            html.append(f'<h3>第{item["position"]}項：{item["name"]}</h3>')
            html.append(f'<p class="advice-content">{item["advice"]}</p>')
            html.append(f'<p class="advice-hint">→ {item["action_hint"]}</p>')
            html.append('</div>')
        html.append('</div>')
        html.append('</section>')
        
        # 6. 展望
        s6 = sections['s6_outlook']
        html.append('<section class="section s6">')
        html.append(f'<h2>6. {s6["title"]} <span class="code">（{meta["zhi_code"]}）</span></h2>')
        html.append('<p class="outlook-intro">如果依照上述建議採取行動，未來的局面將會是：</p>')
        html.append(f'<p class="outlook-content">{s6["content"]}</p>')
        html.append('</section>')
        
        html.append('</main>')
        html.append('</div>')
        
        return "\n".join(html)


class JSONRenderer(YiliRenderer):
    """JSON 渲染（API 用）"""
    
    def render(self, result):
        return json.dumps(result, ensure_ascii=False, indent=2)


class MarkdownRenderer(YiliRenderer):
    """Markdown 渲染"""
    
    def render(self, result):
        lines = []
        meta = result['meta']
        sections = result['sections']
        
        # Header（保留布林碼，移除卦名）
        lines.append("# 易力決策")
        lines.append("")
        if meta.get('question'):
            lines.append(f"**問題**：{meta['question']}")
            lines.append("")
        lines.append(f"- **本卦**：（{meta['ben_code']}）")
        if not meta['is_static']:
            lines.append(f"- **之卦**：（{meta['zhi_code']}）")
            lines.append(f"- **變爻**：{meta['change_positions']}")
        else:
            lines.append("- **之卦**：無變爻（靜卦）")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 1. 現況
        s1 = sections['s1_status']
        lines.append(f"## 1. {s1['title']}（{meta['ben_code']}）")
        lines.append("")
        lines.append(s1['content'])
        lines.append("")
        
        # 2. 變化趨勢
        s2 = sections['s2_trend']
        lines.append(f"## 2. {s2['title']}（{meta['ben_code']}）→（{meta['zhi_code']}）")
        lines.append("")
        lines.append(s2['content'])
        lines.append("")
        
        # 3. 變化過程
        s3 = sections['s3_process']
        if s3:
            lines.append(f"## 3. {s3['title']}（{meta['trans_code']}）")
            lines.append("")
            lines.append(s3['content'])
            lines.append("")
        
        # 4. 六階段
        s4 = sections['s4_stages']
        lines.append(f"## 4. {s4['title']}")
        lines.append("")
        for stage in s4['stages']:
            marker = "⚡ " if stage['is_change'] else ""
            lines.append(f"### {marker}第{stage['position']}階段（{stage['scope']}・{stage['name']}）")
            lines.append("")
            lines.append(stage['content'])
            lines.append("")
        
        # 5. 建議
        s5 = sections['s5_advice']
        lines.append(f"## 5. {s5['title']}")
        lines.append("")
        if s5['is_static']:
            lines.append("目前沒有明顯的變動跡象，六個面向的建議如下：")
        else:
            lines.append("核心考量在於把握以下方向：")
        lines.append("")
        for item in s5['items']:
            lines.append(f"### 第{item['position']}項：{item['name']}")
            lines.append("")
            lines.append(item['advice'])
            lines.append("")
            lines.append(f"> {item['action_hint']}")
            lines.append("")
        
        # 6. 展望
        s6 = sections['s6_outlook']
        lines.append(f"## 6. {s6['title']}（{meta['zhi_code']}）")
        lines.append("")
        lines.append("如果依照上述建議採取行動，未來的局面將會是：")
        lines.append("")
        lines.append(s6['content'])
        lines.append("")
        
        return "\n".join(lines)


# ============================================================
# 使用範例
# ============================================================

if __name__ == "__main__":
    from yili_generator import YiliGenerator
    
    generator = YiliGenerator()
    yao_values = [9, 7, 8, 8, 9, 8]
    result = generator.generate_a1(yao_values)
    
    # 終端機渲染
    print("=== Terminal ===")
    terminal = TerminalRenderer()
    print(terminal.render(result))
