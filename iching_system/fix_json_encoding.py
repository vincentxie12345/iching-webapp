# fix_json_encoding.py
"""
修復 i_ching*.json 檔案的編碼問題
UTF-8 字元被錯誤以 Latin-1 保存，需要轉換回來
"""

import json
import os

def fix_encoding(obj):
    """遞迴修復字典/列表中的字串編碼"""
    if isinstance(obj, str):
        try:
            # UTF-8 字元被當成 Latin-1 保存，轉回來
            return obj.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return obj
    elif isinstance(obj, dict):
        return {fix_encoding(k): fix_encoding(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_encoding(item) for item in obj]
    else:
        return obj


def fix_json_file(input_path, output_path):
    """修復單個 JSON 檔案"""
    print(f"正在修復: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 修復編碼
    fixed_data = fix_encoding(data)
    
    # 驗證
    if '1' in fixed_data:
        print(f"  修復前: {data['1'].get('name', 'N/A')}")
        print(f"  修復後: {fixed_data['1'].get('name', 'N/A')}")
    
    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 已保存: {output_path}")


def main():
    """修復所有 JSON 檔案"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    
    files = [
        'i_ching.json',
        'i_ching_modern.json',
        'i_ching_modern2.json'
    ]
    
    print("="*60)
    print("修復 JSON 編碼")
    print("="*60)
    
    for filename in files:
        input_path = os.path.join(data_dir, filename)
        
        if os.path.exists(input_path):
            # 先備份
            backup_path = input_path + '.backup'
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy(input_path, backup_path)
                print(f"  已備份: {backup_path}")
            
            # 修復並覆蓋
            fix_json_file(input_path, input_path)
        else:
            print(f"  ⚠️ 找不到: {input_path}")
    
    print("="*60)
    print("✅ 修復完成！")
    print("="*60)


if __name__ == "__main__":
    main()
