from openai import OpenAI
import re
from logger import Logger
from configs import Config
import time  # 用于控制请求间隔

logger = Logger()
config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.openai_base_url,
)


def answer(question: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {"role": "system", "content": "请用简练中文回答，避免敏感内容"},
                {"role": "user", "content": f"问题：{question}"},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        ans: str = completion.choices[0].message.content
        logger.info("请求成功！")
        return re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL).strip()
    except Exception as e:
        logger.error(f"API请求失败: {str(e)}")
        time.sleep(1)
        return "当前服务暂不可用，请稍后再试"


def process_questions(questions: list) -> list:
    answers = []
    total_questions = len(questions)
    for index, q in enumerate(questions, start=1):
        logger.info(f"处理中：{index}/{total_questions}")  # 显示当前进度
        ans = answer(q)
        answers.append(ans)
        # time.sleep(0.4)  # 控制请求间隔
    return answers


if __name__ == "__main__":
    # 示例：测试 answer 函数
    test_questions = ["你好，世界！", "今天天气如何？", "什么是人工智能？"]

    answers = process_questions(test_questions)

    for q, a in zip(test_questions, answers):
        print(f"问题: {q}")
        print(f"回答: {a}\n")
