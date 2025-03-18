# 智慧树问答工具

```txt
   ╱|、　　　　　　　　　　　ฅ^•ﻌ•^ฅ
  (˚ˎ 。7　　　　　　　　　　 喵喵感谢~
   |、˜〵　　　　　　　　　 求星星啦~⭐
   じしˍ,)ノ
```

## 环境安装

python>=3.10

```bash
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip install -r requirements.txt
```

## 配置指南

### 📁 配置文件结构

⚠️ 对象键值对使用冒号结构表示 key: value，冒号后面要加一个空格。

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
  - https://qah5.zhihuishu.com/........
  - https://其他课程URL...

OpenAI:
  base_url: "http://localhost:11434/v1"
  api_key: "ollama"
  model: "deepseek-r1:latest"
  max_tokens: 1000
  temperature: 0.3
```

### 🛠️ 核心配置详解

1. 账户认证模块（不填可以用扫码登陆）

   ```yaml
   user:
     name: "student@example.com"
     password: "P@ssw0rd123"
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
     delay_time_s: 10 # 回答问题等待时间(8-15 秒推荐)
     enabled_random_time: True # 启用 ±50%随机偏移

     # 问题筛选模式：
     question_classification: 0 # 0=热门问题 1=最新问题
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
     ......
   ```

4. AI 模型设置

   ```yaml
   OpenAI:
     #api地址
     base_url: "http://localhost:11434/v1"
     # 验证密钥
     api_key: "ollama"
     #模型选择
     model: "deepseek-r1:latest"
     # 生成参数控制：
     max_tokens: 1000 # 回答最大长度(200-1500)
     temperature: 0.3 # 控制模型输出的随机性(0.1-1.0)
   ```

### ▶️ 运行

```bash
  python ./main.py
```

或者可以用
start 脚本
