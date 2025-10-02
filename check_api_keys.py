#!/usr/bin/env python3
"""
Check API key configuration.
"""

import os

def check_api_keys():
    """Check which API keys are configured."""
    print("Checking API Keys Configuration...")
    print("=" * 50)
    
    keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
    }
    
    for key_name, key_value in keys.items():
        if key_value:
            masked_key = key_value[:8] + "*" * (len(key_value) - 12) + key_value[-4:] if len(key_value) > 12 else "*" * len(key_value)
            print(f"[OK] {key_name}: {masked_key}")
        else:
            print(f"[MISSING] {key_name}: Not set")
    
    print("\n" + "=" * 50)
    
    # Check if any keys are set
    has_keys = any(key for key in keys.values())
    if not has_keys:
        print("[WARNING] No API keys found!")
        print("[INFO] Please set the following environment variables:")
        print("  - OPENAI_API_KEY (starts with sk-)")
        print("  - GOOGLE_API_KEY (starts with AIzaSy)")
        print("  - ANTHROPIC_API_KEY (starts with sk-ant-)")
    else:
        print("[INFO] Some API keys are configured")
    
    return keys

if __name__ == "__main__":
    check_api_keys()
