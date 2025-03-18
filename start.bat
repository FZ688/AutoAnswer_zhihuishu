@echo off
REM 关闭命令回显

REM 创建虚拟环境
python -m venv .venv
if %ERRORLEVEL% neq 0 (
    echo 创建虚拟环境失败
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo 激活虚拟环境失败
    exit /b 1
)

REM 更新 pip
python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo 更新 pip 失败
    exit /b 1
)

REM 设置 pip 镜像源
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
if %ERRORLEVEL% neq 0 (
    echo 设置 pip 镜像源失败
    exit /b 1
)

REM 安装依赖
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 安装依赖失败
    exit /b 1
)

REM 运行项目
python ./main.py
if %ERRORLEVEL% neq 0 (
    echo 运行项目失败
    exit /b 1
)

REM 等待用户手动关闭
pause