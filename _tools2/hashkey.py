# 公开仓库不含英文原文：译文以“英文原文的哈希”为键。构建时用玩家自己游戏里的英文算哈希再查表。
import hashlib
def H(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:16]
