import re
import asyncio
from playwright.sync_api import (
    sync_playwright,
    Page,
    Playwright,
    Browser,
    Locator,
    BrowserContext,
)

# from playwright.async_api import async_playwright, Page
from src.configs import Config
from src.logger import Logger
from src.crawler import crawl_popular_question, crawl_latest_question
from src.answer import answer
import time

config = Config()
logger = Logger()


def open_browser(playwright) -> tuple[Browser, BrowserContext]:
    """启动浏览器并返回浏览器和上下文对象
    Args:
        playwright: Playwright实例
    Returns:
        tuple: 包含浏览器实例和上下文对象的元组
    Raises:
        Exception: 浏览器启动失败时抛出异常
    """
    try:
        # 使用Chromium内核启动浏览器
        browser = playwright.chromium.launch(
            channel=config.driver,  # 使用配置中指定的浏览器渠道
            headless=False,  # 可视化模式运行
            args=[
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--start-minimized"  # 启动时最小化
                "--disable-blink-features=AutomationControlled",
            ],  # 禁用自动化检测特征
        )
        # 创建新的浏览器上下文
        context = browser.new_context()
        # 加载反检测脚本（避免被识别为自动化工具）
        with open("scripts/stealth.min.js", "r", encoding="utf-8") as f:
            stealth_js = f.read()
        context.add_init_script(stealth_js)
        return browser, context
    except Exception as e:
        logger.error(f"浏览器启动失败: {e}")
        raise


def login(page: Page) -> Page:
    """登录到智慧树网
    Args:
        page: Playwright页面对象
    Returns:
        Page: 登录成功后的页面对象
    Raises:
        TimeoutError: 操作超时时抛出
        Exception: 登录失败时抛出
    """
    try:
        # 访问登录页面（设置30秒超时）
        page.goto(config.login_url, timeout=30000)
        # 定位未登录状态的登录链接并点击
        login_link = page.locator("#notLogin").get_by_role("link").first
        login_link.click(timeout=10000)

        # 填写用户名和密码
        username_input = page.get_by_role("textbox", name="请输入手机号")
        username_input.fill(str(config.username), timeout=5000)
        password_input = page.get_by_role("textbox", name="请输入密码")
        password_input.fill(str(config.password), timeout=5000)

        # 点击登录按钮
        page.get_by_text("登 录").click(timeout=5000)
        logger.warn("请手动完成验证码验证！")  # 需要人工干预验证码

        # 等待网络空闲（最长等待60秒）
        page.wait_for_load_state("networkidle", timeout=60000)
        logger.info("登录成功！")
        return page
    except TimeoutError as e:
        logger.error(f"登录超时: {e}")
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise


def main():
    with sync_playwright() as playwright:
        try:
            # 初始化浏览器
            browser, context = open_browser(playwright)

            # 登录操作
            login_page = context.new_page()
            login(login_page)
            login_page.close()

            # 遍历课程
            for index, course_url in enumerate(config.courses):
                page = context.new_page()
                try:
                    logger.info(f"开始处理课程 {index+1}/{len(config.courses)}")
                    if config.question_classification == 0:
                        questions = crawl_popular_question(page, course_url)
                    else:
                        questions = crawl_latest_question(page, course_url)
                    answer(page, questions)
                    logger.info(f"成功完成课程: {course_url}")
                except Exception as e:
                    logger.error(f"课程处理失败: {course_url} - {str(e)}")
                finally:
                    page.close()

        finally:
            context.close()
            browser.close()
            print(
                """
   ╱|、　　　　　　　　　　　ฅ^•ﻌ•^ฅ
  (˚ˎ 。7　　　　　　　　　　 喵喵感谢~
   |、˜〵　　　　　　　　　 求星星啦~⭐
   じしˍ,)ノ
问答任务已完成 [✓]
☆ *　. 　☆ ✨ 传送门 ➤https://github.com/xiaozhuABCD1234/AutoAnswer_zhihuishu
　　. ∧＿∧　∩　* ☆ 主人记得给仓库加个星星哦～⭐
* ☆ ( ・∀・)/ .
　. ⊂　　 ノ* ☆
☆ * (つ ノ .☆
　　 (ノ
"""
            )


if __name__ == "__main__":
    main()
