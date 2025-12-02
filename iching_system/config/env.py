# iching_system/config/env.py
"""
環境變數管理
============

管理 API Keys 和系統設定
"""

import os
from pathlib import Path
from typing import Optional


def load_env(env_path: Optional[str] = None):
    """
    載入 .env 檔案
    
    Args:
        env_path: .env 檔案路徑（可選）
    """
    try:
        from dotenv import load_dotenv
        
        if env_path:
            load_dotenv(env_path, override=True)
        else:
            # 自動尋找 .env
            possible_paths = [
                Path.cwd() / '.env',
                Path.cwd().parent / '.env',
                Path(__file__).parent.parent.parent / '.env',
                Path.home() / 'pyprogram' / '.env'
            ]
            
            for path in possible_paths:
                if path.exists():
                    load_dotenv(path, override=True)
                    print(f"✓ 已載入 .env: {path}")
                    break
                    
    except ImportError:
        print("⚠️ 未安裝 python-dotenv，請手動設定環境變數")


def get_api_key(provider: str = 'gemini') -> Optional[str]:
    """
    取得 API Key
    
    Args:
        provider: 'gemini' | 'anthropic'
    """
    if provider == 'gemini':
        return os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    elif provider == 'anthropic':
        return os.getenv('ANTHROPIC_API_KEY')
    else:
        return None


def check_api_keys():
    """檢查 API Keys 設定狀態"""
    gemini = get_api_key('gemini')
    anthropic = get_api_key('anthropic')
    
    print("="*50)
    print("【API Keys 狀態】")
    print("="*50)
    
    if gemini:
        print(f"✅ GEMINI_API_KEY: {gemini[:10]}...{gemini[-4:]}")
    else:
        print("❌ GEMINI_API_KEY: 未設定")
    
    if anthropic:
        print(f"✅ ANTHROPIC_API_KEY: {anthropic[:10]}...{anthropic[-4:]}")
    else:
        print("❌ ANTHROPIC_API_KEY: 未設定")
    
    print("="*50)
    
    return {
        'gemini': bool(gemini),
        'anthropic': bool(anthropic)
    }


def setup_api_key(provider: str, api_key: str):
    """
    設定 API Key（運行時）
    
    Args:
        provider: 'gemini' | 'anthropic'
        api_key: API Key 值
    """
    if provider == 'gemini':
        os.environ['GEMINI_API_KEY'] = api_key
    elif provider == 'anthropic':
        os.environ['ANTHROPIC_API_KEY'] = api_key
    
    print(f"✓ 已設定 {provider.upper()}_API_KEY")
