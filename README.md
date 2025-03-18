# 智慧树问答工具

## 环境安装

python>=3.10

```bash
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple some-package
pip install -r requiremnts.txt
```

## 配置指南

### 📁 配置文件结构

```yaml
# config.yaml
user:
  name: "智慧树登录账号"
  password: "对应密码"

option:
  driver: msedge
  browser_path:
  delay_time_s: 10
  enabled_random_time: True
  question_classification: 0

question-urls:
  - https://qah5.zhihuishu.com/qa.html#/web/home/1000076713
  - https://其他课程URL...

OpenAI:
  base_url: "http://localhost:11434/v1"
  api_key: "ollama"
  model: "deepseek-r1:latest"
  max_tokens: 1000
  temperature: 0.3
```

### 🛠️ 核心配置详解

1. 账户认证模块

   ```yaml
   user:
     name: "student@example.com" # 建议使用手机号登录
     password: "P@ssw0rd123" # 特殊字符需用英文双引号包裹
   ```

2. 浏览器控制模块

   ```yaml
   option:
     # 浏览器类型（必须小写）：
     # [chrome|chrome-beta|chrome-dev|chrome-canary|msedge|msedge-beta...]
     driver: msedge

     # 浏览器执行路径示例：
     # Windows: "C:/Program Files/Google/Chrome/Application/chrome.exe"
     # macOS: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
     browser_path:
     # 延迟设置策略：
     delay_time_s: 10 # 基础等待时间(8-15 秒推荐)
     enabled_random_time: True # 启用 ±50%随机偏移

     # 问题筛选模式：
     question_classification: 0 # 0=高热度问题 1=最新问题
   ```

3. 课程链接配置

   ```yaml
   question-urls:
     # 获取方法：
     # 1. 登录智慧树网页版

     # 2. 进入目标课程问答区

     # 3. 复制浏览器地址栏完整 URL
     - url1
     - url2
     - url3
   ```

4. AI 模型设置

   ```yaml
   OpenAI:
     base_url: "http://localhost:11434/v1" #api地址
     api_key: "ollama" # 验证密钥
     model: "deepseek-r1:latest" #模型选择
     # 生成参数控制：
     max_tokens: 1000 # 回答最大长度(200-1500)
     temperature: 0.3 # 创造力系数(0.1-0.7)
   ```
