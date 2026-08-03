@echo off
chcp 65001 >nul
echo ========================================
echo     旅行规划师 - 启动脚本
echo ========================================
echo.

REM 设置 MSYS2 DLL 路径
set WEASYPRINT_DLL_DIRECTORIES=D:\packet\MSYS2\mingw64\bin

REM 添加 MSYS2 到 PATH
set PATH=D:\packet\MSYS2\mingw64\bin;%PATH%

echo [1/4] 检查 Python 环境...
cd /d "%~dp0"

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [错误] 无法激活虚拟环境
        pause
        exit /b 1
    )
    echo [OK] 虚拟环境已激活
) else (
    echo [警告] 未找到虚拟环境，将使用系统 Python
)

echo [2/4] 环境变量已设置:
echo         WEASYPRINT_DLL_DIRECTORIES=%WEASYPRINT_DLL_DIRECTORIES%
echo         PATH=%PATH%
echo.

echo [3/4] 检查关键依赖...
python -c "import flask; print(f'[OK] Flask {flask.__version__}')" 2>nul
if errorlevel 1 (
    echo [错误] Flask 未安装，请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [4/4] 启动应用...
echo ========================================
echo.

REM 使用新的启动脚本
python run.py

pause
