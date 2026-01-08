"""
Git辅助脚本
解决Windows下Git提交信息中文乱码问题
"""

import subprocess
import sys
import os
from pathlib import Path

def set_git_encoding():
    """设置Git编码配置"""
    configs = [
        ('core.quotepath', 'false'),
        ('i18n.commitencoding', 'utf-8'),
        ('i18n.logoutputencoding', 'utf-8'),
    ]
    
    print("设置Git编码配置...")
    for key, value in configs:
        subprocess.run(['git', 'config', '--global', key, value], check=False)
        print(f"  ✓ {key} = {value}")
    
    print("\n配置完成！")

def commit_with_utf8(message: str):
    """使用UTF-8编码提交"""
    # 设置环境变量
    env = os.environ.copy()
    env['LANG'] = 'zh_CN.UTF-8'
    env['LC_ALL'] = 'zh_CN.UTF-8'
    
    # 执行提交
    subprocess.run(['git', 'commit', '-m', message], env=env, check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        set_git_encoding()
    else:
        print("用法: python scripts/git_helper.py setup")
        print("设置Git编码配置以解决中文乱码问题")
