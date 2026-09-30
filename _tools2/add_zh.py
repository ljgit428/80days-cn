# 读取 "#编号 译文"（每行一条），按 /tmp/todo.json 对齐写入翻译库
#   短碎片（<=12字符）自动只在其作用域生效；"#12@ 译文" 强制作用域；"#12! 译文" 强制全局；"∅" 表示译为空
import json, os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
todo = json.load(open('/tmp/todo.json', encoding='utf-8')); todo_line = json.load(open('/tmp/todo_line.json'))
p = os.path.join(ROOT, 'translation', 'tm_zh.json'); tm = json.load(open(p, encoding='utf-8'))
pl = os.path.join(ROOT, 'translation', 'tm_line.json'); tml = json.load(open(pl, encoding='utf-8')) if os.path.exists(pl) else {}
n = 0; got = set()
for ln in open(sys.argv[1], encoding='utf-8'):
    m = re.match(r'#(\d+)([@!]?)\s?(.*)$', ln.rstrip('\n'))
    if not m: continue
    i = int(m.group(1)); k = todo[i]; z = m.group(3)
    if z == '∅': z = ''
    for tag in ('<i>', '</i>', '<b>', '</b>', '%@'):
        if k.count(tag) != z.count(tag): print('标签不一致', i, repr(k), repr(z))
    if m.group(2) == '@' or (m.group(2) != '!' and len(k.strip()) <= 12): tml.setdefault(todo_line[i], {})[k] = z
    else: tm[k] = z
    n += 1; got.add(i)
json.dump(tm, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(tml, open(pl, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('added', n, '/ todo', len(todo), '| global', len(tm), 'scopes', len(tml))
miss = [i for i in range(len(todo)) if i not in got]
if miss: print('!!! 未提供译文的编号:', miss[:30], '...' if len(miss) > 30 else '')
