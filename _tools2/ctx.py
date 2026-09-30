# 导出带上下文的待译清单，写 /tmp/todo.json（编号 -> 英文）和 /tmp/todo_line.json（编号 -> 作用域）
# 用法: python ctx.py 1-8,14          （ink 行）
#       python ctx.py bb [起始] [个数]  （buildingBlocks，按模块）
# 规则：长文本（>12字符）全局去重；短碎片按作用域去重，且只在该作用域生效
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
def flat(e):
    if isinstance(e, str): return e
    if isinstance(e, list): return ''.join(flat(x) for x in e)
    if isinstance(e, dict):
        if 'option' in e: return '{选项:' + e['option'] + '}'
        if 'action' in e:
            ui = e.get('userInfo') or {}
            return '{' + e['action'] + ':' + ' | '.join(str(ui[k]) for k in ACTION_TEXT.get(e['action'], ()) if k in ui) + '}'
        if 'condition' in e and ('then' in e or 'otherwise' in e):
            return '{IF:' + flat(e.get('then', [])) + '|ELSE:' + flat(e.get('otherwise', [])) + '}'
        if 'buildingBlock' in e: return '{BB:' + e['buildingBlock'] + '}'
        if 'divert' in e: return ''
        for k in ('cycle', 'sequence', 'shuffle', 'onceonly'):
            if k in e: return '{' + k + ':' + ' / '.join(flat(x) for x in e[k]) + '}'
    return ''
def short(s): return len(s.strip()) <= 12
if __name__ == '__main__':
    tm = json.load(open(os.path.join(ROOT, 'translation', 'tm_zh.json'), encoding='utf-8'))
    pl = os.path.join(ROOT, 'translation', 'tm_line.json'); tml = json.load(open(pl, encoding='utf-8')) if os.path.exists(pl) else {}
    units = []   # (作用域, 标题, 节点, 展示文本)
    if sys.argv[1] == 'bb':
        bb = json.load(open(os.path.join(EXT, '80days'), encoding='utf-8'))['buildingBlocks']
        skip = set(json.load(open(os.path.join(ROOT, 'translation', 'bb_override.json'), encoding='utf-8')))
        names = [k for k in bb if k not in skip]
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 0; n = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
        for k in names[a:a + n]: units.append(('bb:' + k, f'BB {k}', bb[k], flat(bb[k])))
    else:
        lines = open(os.path.join(EXT, '80days.inkcontent'), encoding='utf-8').read().split('\n')
        for part in sys.argv[1].split(','):
            a, _, b = part.partition('-')
            for i in range(int(a), int(b or a) + 1):
                d = json.loads(lines[i])
                parts = d.get('stitches',{}).items() if isinstance(d, dict) else [('-', {'content': d})]
                units.append((str(i), f'行 {i}', d, '\n'.join(f'[{k}] ' + flat(v['content']) for k, v in parts)))
    todo, todo_line, seen = [], [], set()
    for sc, title, node, shown in units:
        new = []
        def cb(s, p):
            if s in tm or s in tml.get(sc, {}) or (sc.startswith('bb:') and s in tml.get('bb', {})): return
            key = (sc, s) if short(s) else s
            if key in seen: return
            seen.add(key); todo.append(s); todo_line.append(sc); new.append(len(todo) - 1)
        walk_ink(node, cb, '/bb' if sc.startswith('bb:') else '')
        if not new: continue
        print(f'==== {title}'); print(shown.replace('<br><br>', '¶')[:4000])
        for n_ in new: print(f'  #{n_} {json.dumps(todo[n_], ensure_ascii=False)}')
    json.dump(todo, open('/tmp/todo.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(todo_line, open('/tmp/todo_line.json', 'w'))
    print('TODO', len(todo), sum(map(len, todo)), file=sys.stderr)
