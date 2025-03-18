import random
import time


def get_random(n: int) -> int:
    random.seed(time.time())
    return random.randint(int(n / 2), int(n * 1.5))


# start_time = time.time()  # 总开始时间
# time.sleep(1)
# total_time = time.time() - start_time  # 计算总耗时

# print(
#     f"""
#    ╱|、　　　　　　　　　　　ฅ^•ﻌ•^ฅ
#   (˚ˎ 。7　　　　　　　　　　喵喵感谢~
#    |、˜〵　　　　　　　　　 耗时{total_time:.1f}秒~
#    じしˍ,)ノ
# 问答任务已完成 [✓]
# ☆ *　. 　☆ ✨ 传送门 ➤https://github.com/xiaozhuABCD1234/AutoAnswer_zhihuishu
# 　　. ∧＿∧　∩　* ☆ 主人记得给仓库加个星星哦～⭐
# * ☆ ( ・∀・)/ .
# 　. ⊂　　 ノ* ☆
# ☆ * (つ ノ .☆
# 　　 (ノ
# """
# )
