import sys, io, json, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
lines = raw.split('\n')

acts = Counter()
text_actions = []
RANGES = [(0, 31), (785, 801), (1174, 1177)]

def walk(el, lineno):
    if isinstance(el, dict):
        if 'action' in el:
            acts[el['action']] += 1
            ui = el.get('userInfo')
            if isinstance(ui, dict):
                for k, v in ui.items():
                    if isinstance(v, str) and re.search(r'[A-Za-z]', v) and len(v) > 3:
                        # 排除纯标识符
                        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', v):
                            text_actions.append((lineno, el['action'], k, v))
        for k, v in el.items():
            walk(v, lineno)
    elif isinstance(el, list):
        for x in el:
            walk(x, lineno)

for a, b in RANGES:
    for i in range(a, min(b, len(lines))):
        ln = lines[i]
        if not ln.strip():
            continue
        walk(json.loads(ln), i)

print('=== action 类型统计 ===')
for k, v in acts.most_common():
    print(f'  {k}: {v}')
print('\n=== action 内文本（前 40） ===')
for t in text_actions[:40]:
    print(f'  L{t[0]} [{t[1]}.{t[2]}] {t[3][:100]!r}')
print('总数:', len(text_actions))
