from openai import OpenAI
import re
from src.logger import Logger
from src.configs import Config
import time
from playwright.sync_api import Page
from src.utils import get_random

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
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        ans: str = completion.choices[0].message.content
        logger.info("请求成功！")
        ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL).strip()
        logger.info(f"回答：{ans}")
        return ans
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


def upload_answer(page: Page, q: str) -> bool:
    """协调各个步骤的上传回答流程"""
    page2 = open_answer_page(page, q)
    if not page2:
        return False

    try:
        if check_had_answered(page2):
            return False
        elif not click_answer_button(page2):
            return False
        a: str = get_answer(q)
        if not fill_answer_content(page2, a):
            return False

        return submit_answer(page2)
    finally:
        # 确保无论成功与否都会关闭页面（如果未被提前关闭）
        if "page2" in locals() and page2:
            page2.close()


def open_answer_page(page: Page, question: str) -> Page | None:
    try:
        with page.expect_popup() as page2_info:
            page.get_by_text(question).click()
        return page2_info.value
    except Exception as e:
        logger.error(f"打开回答页面失败: {e}")
        return None


def check_had_answered(page: Page) -> bool:
    # 等待页面加载完成，确保所有网络请求都已完成
    page.wait_for_load_state("networkidle")
    
    if not page.locator("div").filter(has_text="我来回答").nth(2).is_visible():
        logger.warn("没有找到“我来回答”按钮，你可能已经回答了。")
        return True
    else:
        return False

def click_answer_button(page2: Page) -> bool:
    """点击“我来回答”按钮"""
    try:
        page2.locator("div").filter(has_text="我来回答").nth(2).click()
        return True
    except Exception as e:
        logger.error(f"点击“我来回答”失败: {e}")
        return False


def fill_answer_content(page2: Page, answer: str) -> bool:
    """填写回答内容"""
    try:
        textbox = page2.get_by_role("textbox", name="请输入您的回答")
        textbox.click()
        time.sleep(get_random(config.delay_time_s) // 2)
        textbox.fill(answer)
        time.sleep(get_random(config.delay_time_s) // 2)
        return True
    except Exception as e:
        logger.error(f"填写回答失败: {e}")
        return False


def submit_answer(page2: Page) -> bool:
    """提交回答并关闭页面"""
    try:
        page2.get_by_text("立即发布").click()
        page2.close()
        return True
    except Exception as e:
        logger.error(f"提交回答失败: {e}")
        page2.close()
        return False


def answer(page: Page, questions: list[str]) -> None:
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        logger.info(f"处理中：{index}/{total_questions}")
        logger.info(f"问题{index}：{question}")
        if not upload_answer(page, question):
            logger.warn(f"问题{index}处理失败，跳过")
            continue


# if __name__ == "__main__":
#     # 示例：测试 answer 函数
#     test_questions = ["你好，世界！", "今天天气如何？", "什么是人工智能？"]

#     answers = process_questions(test_questions)

#     for q, a in zip(test_questions, answers):
#         print(f"问题: {q}")
#         print(f"回答: {a}\n")
