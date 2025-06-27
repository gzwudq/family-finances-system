import os
import subprocess
import sys

def build_exe():
    """打包程序为exe文件"""
    print("开始打包家庭收入管理系统...")
    
    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',  # 打包成单个exe文件
        '--windowed',  # 不显示控制台窗口
        '--name=家庭收入管理系统',  # exe文件名
        '--icon=icon.ico',  # 图标文件（如果有的话）
        '--add-data=family_finance.db;.',  # 包含数据库文件
        '--hidden-import=tkinter',
        '--hidden-import=sqlite3',
        '--hidden-import=datetime',
        '--hidden-import=locale',
        '--hidden-import=csv',
        '--hidden-import=os',
        '--hidden-import=math',
        'main.py'
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 打包成功！")
            print("exe文件位置: dist/家庭收入管理系统.exe")
            print("你可以将dist文件夹中的exe文件分发给其他用户使用。")
        else:
            print("❌ 打包失败！")
            print("错误信息:", result.stderr)
            
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {e}")

if __name__ == "__main__":
    build_exe() 