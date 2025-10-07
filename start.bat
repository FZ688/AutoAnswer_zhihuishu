@echo off
REM 关闭命令回显

REM 使用 UTF-8 输出，避免中文乱码
chcp 65001 >nul


REM 创建虚拟环境
python -m venv .venv
if %ERRORLEVEL% neq 0 (
    echo 创建虚拟环境失败
    pause
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)


REM 更新 pip（使用 venv 的 python -m pip 确保目标在虚拟环境）
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo 更新 pip 失败
    pause
    exit /b 1
)


REM 安装依赖，优先使用 --isolated 忽略用户/全局配置（保护本机设置不被修改）
python -m pip install --isolated -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 首次安装失败（--isolated 模式），尝试不使用 --isolated 重新安装
    python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo 安装依赖失败
        pause
        exit /b 1
    )
)

REM 运行项目
python ./main.py
if %ERRORLEVEL% neq 0 (
    echo 运行项目失败
    pause
    exit /b 1
)

REM 等待用户手动关闭
pause