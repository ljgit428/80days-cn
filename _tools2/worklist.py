# 按剧情顺序导出某些行的待译字符串（去重、跳过已译）
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
def load_tm():
    p = os.path.join(ROOT, 'translation', 'tm_zh.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
def ink_strings(idx_list):
    lines = open(os.path.join(EXT, '80days.inkcontent'), encoding='utf-8').read().split('\n')
    seen = []; s = set()
    for i in idx_list:
        def cb(x, p):
            if x not in s: s.add(x); seen.append((i, x))
        walk_ink(json.loads(lines[i]), cb)
    return seen
if __name__ == '__main__':
    idx = []
    for part in sys.argv[1].split(','):
        a, _, b = part.partition('-'); idx += list(range(int(a), int(b or a) + 1))
    tm = load_tm()
    todo = [(i, x) for i, x in ink_strings(idx) if x not in tm]
    print(len(todo), sum(len(x) for _, x in todo), file=sys.stderr)
    json.dump([x for _, x in todo], open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
