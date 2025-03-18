# 创建并激活虚拟环境
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Error "创建虚拟环境失败"
    exit 1
}

# 激活虚拟环境
if ($IsWindows) {
    .\.venv\Scripts\activate
} else {
    .\.venv\bin\activate
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "激活虚拟环境失败"
    exit 1
}

# 更新 pip
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Error "更新 pip 失败"
    exit 1
}

# 设置 pip 镜像源
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
if ($LASTEXITCODE -ne 0) {
    Write-Error "设置 pip 镜像源失败"
    exit 1
}

# 安装依赖
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "安装依赖失败"
    exit 1
}

# 运行项目
python ./main.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "运行项目失败"
    exit 1
}

# 等待用户手动关闭
Write-Host "按任意键退出..."
Read-Host