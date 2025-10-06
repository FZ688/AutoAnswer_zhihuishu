from openai import OpenAI
import re
import asyncio
from src.logger import Logger
from src.configs import Config
import time
from playwright.async_api import Page
from src.utils import get_random
import traceback
import inspect

logger = Logger()
config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.openai_base_url,
)


async def get_answer(question: str) -> str:
    # 将同步的 OpenAI 调用放到线程池中执行，避免对非 awaitable 对象使用 await
    def _sync_call(q: str) -> str:
        try:
            completion = client.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个严谨的中文学生，请你回答同学的问题来帮助同学，回答需满足：\n1. 用口语化中文，50字内分点回答\n2. 回答需要符合中国特色社会主义核心价值观，回避暴力、伦理等敏感内容\n4. 禁用Markdown格式\n请确保内容符合中国法律法规。",
                    },
                    {"role": "user", "content": f"问题：{q}"},
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
            # 不同 OpenAI 客户端版本返回的数据结构可能不同，兼容取值
            try:
                return completion.choices[0].message.content
            except Exception:
                # 回退：如果返回原始文本字段不同
                return str(completion)
        except Exception as e:
            logger.error(f"API 请求（线程）失败: {e}")
            return "当前服务暂不可用，请稍后再试"

    ans = await asyncio.to_thread(_sync_call, question)
    try:
        logger.info("请求成功！")
        ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.DOTALL).strip()
        logger.info(f"回答：{ans}")
    except Exception:
        # 若处理回答时出错，仍返回原始字符串
        logger.error("处理回答文本时发生错误",)
    return ans


async def process_questions(questions: list) -> list:
    answers = []
    total_questions = len(questions)
    for index, q in enumerate(questions, start=1):
        logger.info(f"处理中：{index}/{total_questions}")  # 显示当前进度
        ans = await get_answer(q)
        answers.append(ans)
    return answers


async def upload_answer(page: Page, q: str) -> bool:
    """协调各个步骤的上传回答流程
    增加防御性检查，避免对 None 使用 await，并在发生 TypeError 时记录完整 traceback
    """
    page2 = await open_answer_page(page, q)
    if not page2:
        logger.warn("未能打开回答页面（page2 为 None），跳过该题")
        return False

    try:
        # 额外类型检查，确保 page2 是 Playwright 的 Page 对象（简单判断）
        if not hasattr(page2, 'goto'):
            logger.error(f"open_answer_page 返回的 page2 无 goto 方法，类型={type(page2)}，跳过")
            return False

        try:
            had = await check_had_answered(page2)
        except TypeError as te:
            logger.error("检查是否已回答时发生 TypeError，详细信息：")
            logger.error(traceback.format_exc())
            return False

        if had:
            return False

        try:
            clicked = await click_answer_button(page2)
        except TypeError:
            logger.error("点击回答按钮时发生 TypeError，详细信息：")
            logger.error(traceback.format_exc())
            return False

        if not clicked:
            return False

        # 获取回答（网络请求）
        a: str = await get_answer(q)
        if not a:
            logger.warn("未获取到回答内容，跳过该题")
            return False

        try:
            filled = await fill_answer_content(page2, a)
        except TypeError:
            logger.error("填写回答内容时发生 TypeError，详细信息：")
            logger.error(traceback.format_exc())
            return False

        if not filled:
            return False

        try:
            return await submit_answer(page2)
        except TypeError:
            logger.error("提交回答时发生 TypeError，详细信息：")
            logger.error(traceback.format_exc())
            return False
    finally:
        # 确保无论成功与否都会关闭页面（如果未被提前关闭）
        if "page2" in locals() and page2:
            try:
                await page2.close()
            except Exception:
                pass


async def open_answer_page(page: Page, question: str) -> Page | None:
    try:
        locator = page.get_by_text(question)
        # 确保元素可见并滚动到视野中
        try:
            await locator.scroll_into_view_if_needed()
            await locator.wait_for(state="visible", timeout=5000)
        except Exception:
            logger.warn(f"问题元素不可见或等待超时: {question}")

        context = page.context
        before_pages = list(context.pages)

        # 尝试通过弹窗打开（最常见）
        try:
            async with page.expect_popup(timeout=5000) as page2_info:
                await locator.click()
            page2_candidate = page2_info.value
            page2 = await page2_candidate if inspect.isawaitable(page2_candidate) else page2_candidate
            logger.info(f"打开弹窗成功，类型={type(page2)}")
            return page2
        except Exception as popup_exc:
            logger.info(f"expect_popup 未捕获到弹窗或点击失败: {popup_exc}; 尝试后备策略...")
            # 后备策略 1: 从元素取 href 并在新标签打开
            try:
                href = await locator.get_attribute("href")
                if href:
                    new_page = await context.new_page()
                    await new_page.goto(href)
                    logger.info(f"通过 href 打开新页面: {href}")
                    return new_page
            except Exception:
                pass

            # 后备策略 2: 检查是否有新的 page 出现
            after_pages = list(context.pages)
            new_pages = [p for p in after_pages if p not in before_pages]
            if new_pages:
                logger.info(f"在 context 中检测到新页面，返回新页面类型={type(new_pages[0])}")
                return new_pages[0]

            # 后备策略 3: 点击可能导致当前页面导航（无弹窗），尝试再次点击并观察 URL
            try:
                await locator.click()
                await page.wait_for_load_state("networkidle", timeout=5000)
                logger.info("点击后在同一页面导航，返回当前页面对象")
                return page
            except Exception as final_exc:
                logger.error(f"点击并检测导航也失败: {final_exc}")
                return None
    except Exception as e:
        logger.error(f"打开回答页面失败: {e}")
        return None


async def check_had_answered(page: Page) -> bool:
    # 等待页面加载完成，确保所有网络请求都已完成
    await page.wait_for_load_state("networkidle")

    if not await page.locator("div").filter(has_text="我来回答").nth(2).is_visible():
        logger.warn("没有找到“我来回答”按钮，你可能已经回答了。")
        return True
    else:
        return False


async def click_answer_button(page2: Page) -> bool:
    """点击“我来回答”按钮"""
    try:
        await page2.locator("div").filter(has_text="我来回答").nth(2).click()
        return True
    except Exception as e:
        logger.error(f"点击“我来回答”失败: {e}")
        return False


async def fill_answer_content(page2: Page, answer: str) -> bool:
    """填写回答内容"""
    try:
        # get_by_role 返回 Locator（非 awaitable），不要对其使用 await
        textbox = page2.get_by_role("textbox", name="请输入您的回答")
        await textbox.click()
        if(config.enabled_random_time):
            await asyncio.sleep(get_random(config.delay_time_s) // 2)
        else:
            await asyncio.sleep(config.delay_time_s//2)
        await textbox.fill(answer)
        return True
    except Exception as e:
        logger.error(f"填写回答失败: {e}")
        return False


async def submit_answer(page2: Page) -> bool:
    """提交回答并关闭页面"""
    try:
        await page2.get_by_text("立即发布").click()
        if(config.enabled_random_time):
            await asyncio.sleep(get_random(config.delay_time_s) // 2)
        else:
            await asyncio.sleep(config.delay_time_s//2)
        logger.info("发布成功")
        await page2.close()
        return True
    except Exception as e:
        logger.error(f"提交回答失败: {e}")
        await page2.close()
        return False


async def answer(page: Page, questions: list[str]) -> None:
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        logger.info(f"处理中：{index}/{total_questions}")
        logger.info(f"问题{index}：{question}")
        if not await upload_answer(page, question):
            logger.warn(f"问题{index}处理失败，跳过")
            continue

if __name__ == "__main__":
    # 测试
    test_questions = ["你好，世界！", "今天天气如何？", "什么是人工智能？"]

    answers = asyncio.run(process_questions(test_questions))

    for q, a in zip(test_questions, answers):
        print(f"问题: {q}")
        print(f"回答: {a}\n")
        print(f"回答: {a}\n")
