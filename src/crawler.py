from playwright.async_api import (
    async_playwright,
    Page,
)
import asyncio
import inspect
from src.logger import Logger

logger = Logger()


async def crawl_popular_question(page: Page, url: str) -> list[str]:
    """爬取热门问题
    Args:
        page: 已登录的页面对象
        url: 目标页面URL
    Returns:
        list[str]: 问题文本列表
    Raises:
        多种异常: 包含超时、元素未找到等错误
    """
    try:
        # 访问目标页面（设置2分钟超时）
        await page.goto(url, timeout=120000)
        await page.wait_for_load_state("networkidle", timeout=120000)  # 等待网络空闲

        # 等待问题容器加载（最多等待60秒）
        await page.wait_for_selector(".question-item", timeout=60000)
        questions = await page.query_selector_all(".question-item")

        # 问题容器检测
        if not questions:
            raise ValueError("未检测到题目容器，请检查页面结构！")

        # 解析问题内容
        question_texts = []
        # 辅助函数：如果对象是 coroutine 则 await 后返回，否则直接返回对象
        async def _maybe_await(obj):
            # 使用 inspect.isawaitable 更通用地判断是否可等待
            if inspect.isawaitable(obj):
                return await obj
            return obj
        for question_element in questions:
            # 防护：question_element 有时可能是 coroutine，先确保它被 await
            question_element = await _maybe_await(question_element)
            # 定位问题内容区域
            content_div = await question_element.query_selector(
                ".question-content.ZHIHUISHU_QZMD"
            )
            if content_div:
                # 提取纯文本内容并去除首尾空格（防护：处理意外的 coroutine）
                content_div = await _maybe_await(content_div)
                try:
                    # inner_text 通常是协程，先获得可能的协程对象再 await
                    text_raw = content_div.inner_text()
                    text = (await _maybe_await(text_raw)).strip()
                except AttributeError as ae:
                    # 如果出现 'coroutine' object has no attribute 'inner_text'，记录类型并尝试 await 后重试
                    logger.error(f"content_div 属性错误，类型={type(content_div)}，异常={ae}")
                    content_div = await _maybe_await(content_div)
                    text_raw = content_div.inner_text()
                    text = (await _maybe_await(text_raw)).strip()
                question_texts.append(text)
            else:
                logger.warning("某个问题项未找到问题内容容器")

        logger.info(f"成功解析 {len(question_texts)} 道热门题目")
        return question_texts

    except TimeoutError as e:
        logger.error(f"页面加载超时: {url} - {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"页面解析错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理页面 {url} 时发生未知错误: {str(e)}")
        raise


async def crawl_latest_question(page: Page, url: str) -> list[str]:
    """爬取最新问题（与热门问题逻辑相似，增加排序操作）
    Args:
        page: 已登录的页面对象
        url: 目标页面URL
    Returns:
        list[str]: 问题文本列表
    """
    try:
        await page.goto(url, timeout=120000)
        await page.wait_for_load_state("networkidle", timeout=120000)
        await page.wait_for_selector(".question-item", timeout=60000)

        # 点击"最新"排序标签（核心差异点）
        await page.get_by_text("最新").click()
        await page.wait_for_load_state("networkidle")  # 等待排序后的内容加载
        await page.wait_for_selector(".question-item", timeout=60000)

        # 后续解析逻辑与热门问题相同
        questions = await page.query_selector_all(".question-item")
        if not questions:
            raise ValueError("未检测到题目容器，请检查页面结构！")

        question_texts = []
        async def _maybe_await(obj):
            if inspect.isawaitable(obj):
                return await obj
            return obj
        for question_element in questions:
            question_element = await _maybe_await(question_element)
            content_div = await question_element.query_selector(
                ".question-content.ZHIHUISHU_QZMD"
            )
            if content_div:
                content_div = await _maybe_await(content_div)
                try:
                    text_raw = content_div.inner_text()
                    text = (await _maybe_await(text_raw)).strip()
                except AttributeError as ae:
                    logger.error(f"content_div 属性错误，类型={type(content_div)}，异常={ae}")
                    content_div = await _maybe_await(content_div)
                    text_raw = content_div.inner_text()
                    text = (await _maybe_await(text_raw)).strip()
                question_texts.append(text)
            else:
                logger.warning("某个问题项未找到问题内容容器")

        logger.info(f"成功解析 {len(question_texts)} 道最新题目")
        return question_texts

    except TimeoutError as e:
        logger.error(f"页面加载超时: {url} - {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"页面解析错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理页面 {url} 时发生未知错误: {str(e)}")
        raise
