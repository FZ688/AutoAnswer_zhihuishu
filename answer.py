from openai import OpenAI
import re
from logger import Logger
from configs import Config
import time
from playwright.sync_api import Page

logger = Logger()
config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.openai_base_url,
)


def get_answer(question: str) -> str:
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
        return "当前服务暂不可用，请稍后再试"


def process_questions(questions: list) -> list:
    answers = []
    total_questions = len(questions)
    for index, q in enumerate(questions, start=1):
        logger.info(f"处理中：{index}/{total_questions}")  # 显示当前进度
        ans = get_answer(q)
        answers.append(ans)
    return answers


def upload_answer(page: Page, q: str, a: str) -> None:
    with page.expect_popup() as page2_info:
        page.get_by_text(q).click()
    page2 = page2_info.value
    page2.locator("div").filter(has_text="我来回答").nth(2).click()
    page2.get_by_role("textbox", name="请输入您的回答").click()
    time.sleep(config.delay_time_s / 2)
    page2.get_by_role("textbox", name="请输入您的回答").fill(a)
    time.sleep(config.delay_time_s / 2)
    page2.get_by_text("立即发布").click()
    page2.close()


def answer(page: Page, questions: list[str]) -> None:
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        logger.info(f"处理中：{index}/{total_questions}")
        logger.info(f"问题{index}：{question}")
        answer: str = get_answer(question)
        logger.info(f"回答{index}：{answer}")
        upload_answer(page, question, answer)


# if __name__ == "__main__":
#     # 示例：测试 answer 函数
#     test_questions = ["你好，世界！", "今天天气如何？", "什么是人工智能？"]

#     answers = process_questions(test_questions)

#     for q, a in zip(test_questions, answers):
#         print(f"问题: {q}")
#         print(f"回答: {a}\n")
