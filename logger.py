import time
import threading


class Logger:
    _instance = None
    _lock = threading.Lock()  # 线程安全锁

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._init()
        return cls._instance

    def _init(self):
        pass  # 移除不必要的文件夹创建逻辑

    def _get_date(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def info(self, msg, line_break=False):
        self._log("[INFO]", "\033[32m", msg, line_break)

    def warn(self, msg, line_break=False):
        self._log("[WARN]", "\033[33m", msg, line_break)

    def error(self, msg, line_break=False):
        self._log("[ERROR]", "\033[31m", msg, line_break)

    def _log(self, level, color, msg, line_break):
        current_time = self._get_date()
        formatted_msg = f"[{current_time}] {level} {msg}"

        if line_break:
            print(f"\n{color}{formatted_msg}\033[0m")
        else:
            print(f"{color}{formatted_msg}\033[0m")

    def debug(self, msg, line_break=False):
        """添加调试日志等级"""
        self._log("[DEBUG]", "\033[34m", msg, line_break)

    def critical(self, msg, line_break=False):
        """添加严重错误日志等级"""
        self._log("[CRITICAL]", "\033[31m\033[1m", msg, line_break)
