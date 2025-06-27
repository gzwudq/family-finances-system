@echo off
echo 正在打包家庭收入管理系统为exe文件...
echo.

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM 执行打包命令
pyinstaller --onefile --windowed --name="家庭收入管理系统" --add-data="family_finance.db;." main.py

echo.
if exist dist\家庭收入管理系统.exe (
    echo ✅ 打包成功！
    echo exe文件位置: dist\家庭收入管理系统.exe
    echo 文件大小: 
    dir dist\家庭收入管理系统.exe | find "家庭收入管理系统.exe"
) else (
    echo ❌ 打包失败！
)

echo.
pause 