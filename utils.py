import random
import time


# 使用当前时间的时间戳作为种子
def get_random(n: int) -> int:
    random.seed(time.time())
    return random.randint(int(n / 2), int(n * 1.5))
