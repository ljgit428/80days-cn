# 检查指定行还有哪些字符串没有译文（同时考虑全局 TM 和按行 TM）
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
tm = json.load(open(os.path.join(ROOT, 'translation', 'tm_zh.json'), encoding='utf-8'))
pl = os.path.join(ROOT, 'translation', 'tm_line.json'); tml = json.load(open(pl, encoding='utf-8')) if os.path.exists(pl) else {}
lines = open(os.path.join(EXT, '80days.inkcontent'), encoding='utf-8').read().split('\n')
idx = []
for part in sys.argv[1].split(','):
    a, _, b = part.partition('-'); idx += list(range(int(a), int(b or a) + 1))
bad = 0
for i in idx:
    miss = []
    walk_ink(json.loads(lines[i]), lambda s, p: miss.append(s) if s not in tm and s not in tml.get(str(i), {}) and s not in miss else None)
    if miss: bad += 1; print(i, miss)
print('未完成行数', bad, '/', len(idx))
