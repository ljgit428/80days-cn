# 扫描全部可翻译文本，生成 translation/source.json（去重的英文 + 出现位置 + 上下文）
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *
entries = collections.OrderedDict()
def add(s, where):
    e = entries.setdefault(s, {'en': s, 'n': 0, 'at': []})
    e['n'] += 1
    if len(e['at']) < 3: e['at'].append(where)

lines = open(os.path.join(EXT, '80days.inkcontent'), encoding='utf-8').read().split('\n')
for i, ln in enumerate(lines):
    if ln.strip():
        walk_ink(json.loads(ln), lambda s, p: add(s, f'ink:{i}'))
bb = json.load(open(os.path.join(EXT, '80days'), encoding='utf-8'))['buildingBlocks']
for k, v in bb.items():
    walk_ink(v, lambda s, p: add(s, f'bb:{k}'), '/bb')
for f, keys in DATA_RULES.items():
    d = json.load(open(os.path.join(EXT, f), encoding='utf-8'))
    walk_data(d, keys, lambda s, p: add(s, f'{f}:{p[:60]}'))
out = list(entries.values())
os.makedirs(os.path.join(ROOT, 'translation'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'translation', 'source.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
by = collections.Counter(e['at'][0].split(':')[0] for e in out)
print('unique', len(out), 'chars', sum(len(e['en']) for e in out), dict(by))
