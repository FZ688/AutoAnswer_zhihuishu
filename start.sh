#!/bin/bash

# 创建并激活虚拟环境
python -m venv .venv
if [ $? -ne 0 ]; then
    echo "创建虚拟环境失败" >&2
    exit 1
fi

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
if [ $? -ne 0 ]; then
    echo "激活虚拟环境失败" >&2
    exit 1
fi

# 更新 pip
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "更新 pip 失败" >&2
    exit 1
fi

# 设置 pip 镜像源
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
if [ $? -ne 0 ]; then
    echo "设置 pip 镜像源失败" >&2
    exit 1
fi

# 安装依赖
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "安装依赖失败" >&2
    exit 1
fi

# 运行项目
python ./main.py
if [ $? -ne 0 ]; then
    echo "运行项目失败" >&2
    exit 1
fi

# 等待用户手动关闭
read -p "按任意键退出..."
