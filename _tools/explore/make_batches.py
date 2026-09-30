import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
lines = raw.split('\n')
RANGES = [(0, 31), (785, 801), (1174, 1177)]

import re
def is_identifier(s):
    s = s.strip()
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', s):
        return False
    if '_' in s: return True
    if re.search(r'[a-z][A-Z]', s): return True
    if re.search(r'[A-Z]{2,}[a-z]', s): return True
    return False

def has_letters(s):
    t = re.sub(r'<[^>]+>', '', s)
    return bool(re.search(r'[A-Za-z]', t)) and t.strip()

ACTION_TEXT_FIELDS = {
    'Incident': ('text',),
    'SetClue': ('text', 'speaker'),
    'ChangeTransportTitle': ('title',),
}

def walk(el, lineno, path, out):
    if isinstance(el, str):
        if path and has_letters(el) and not is_identifier(el):
            out.append(el)
    elif isinstance(el, list):
        for x in el:
            walk(x, lineno, path, out)
    elif isinstance(el, dict):
        if 'action' in el:
            act = el['action']
            if act in ACTION_TEXT_FIELDS:
                ui = el.get('userInfo') or {}
                if isinstance(ui, dict):
                    for f in ACTION_TEXT_FIELDS[act]:
                        if f in ui and isinstance(ui[f], str) and has_letters(ui[f]) and not is_identifier(ui[f]):
                            out.append(ui[f])
        for k, v in el.items():
            if k in ('initial','linkPath','divert','func','get','var','name','buildingBlock','condition','params','action','userInfo','set','doFuncs'):
                continue
            walk(v, lineno, path + '/' + k, out)

# 收集每行
row_tasks = []
for a, b in RANGES:
    for i in range(a, min(b, len(lines))):
        ln = lines[i]
        if not ln.strip():
            continue
        d = json.loads(ln)
        strs = []
        walk(d, i, '', strs)
        if not strs:
            continue
        # 去重保序
        seen = set(); uniq = []
        for s in strs:
            if s not in seen:
                seen.add(s); uniq.append(s)
        row_tasks.append({'line': i, 'strings': uniq})

print('行任务数:', len(row_tasks))
total_chars = sum(sum(len(s) for s in t['strings']) for t in row_tasks)
print('待翻译总字符:', total_chars)

# 按字符数分批，每批约 9000 字符
BATCH = 9000
batches = []
cur = []; cur_n = 0
for t in row_tasks:
    n = sum(len(s) for s in t['strings'])
    if cur and cur_n + n > BATCH:
        batches.append(cur); cur = []; cur_n = 0
    cur.append(t); cur_n += n
if cur:
    batches.append(cur)

print('批次数:', len(batches))
for i, b in enumerate(batches):
    print(f'  批 {i}: {len(b)} 行, {sum(len(s) for t in b for s in t["strings"])} 字符, 行号 {b[0]["line"]}-{b[-1]["line"]}')

os.makedirs(r'D:\git\project\80 days CN\translation', exist_ok=True)
# 保存每行的 JSON（供代理读上下文）
line_json = {}
for t in row_tasks:
    line_json[t['line']] = lines[t['line']]

# 分批数据：每批含行的 json
batch_data = []
for b in batches:
    items = []
    for t in b:
        items.append({'line': t['line'], 'strings': t['strings'], 'json': lines[t['line']]})
    batch_data.append(items)

json.dump(batch_data, open(r'D:\git\project\80 days CN\translation\batches.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('saved batches.json')
print('batches.json size:', os.path.getsize(r'D:\git\project\80 days CN\translation\batches.json'))
