import sys, io, json, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
lines = raw.split('\n')

RANGES = [(0, 31), (785, 801), (1174, 1177)]

def is_identifier(s):
    s = s.strip()
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', s):
        return False
    if '_' in s:
        return True
    if re.search(r'[a-z][A-Z]', s):
        return True
    if re.search(r'[A-Z]{2,}[a-z]', s):
        return True
    return False

def has_letters(s):
    return bool(re.search(r'[A-Za-z]', re.sub(r'<[^>]+>', '', s))) and re.sub(r'<[^>]+>', '', s).strip()

# action 里可翻译的 userInfo 字段
ACTION_TEXT_FIELDS = {
    'Incident': ('text',),
    'SetClue': ('text', 'speaker'),
    'ChangeTransportTitle': ('title',),
}

entries = {}

def add(s, lineno, where):
    s = s
    if not has_letters(s):
        return
    if is_identifier(s):
        return
    if s not in entries:
        entries[s] = {'n': 0, 'ctx': []}
    entries[s]['n'] += 1
    if len(entries[s]['ctx']) < 2:
        entries[s]['ctx'].append(f'L{lineno} {where}')

def walk(el, lineno, path=''):
    if isinstance(el, str):
        if path:
            add(el, lineno, path[-46:])
    elif isinstance(el, list):
        for x in el:
            walk(x, lineno, path)
    elif isinstance(el, dict):
        if 'action' in el:
            act = el['action']
            if act in ACTION_TEXT_FIELDS:
                ui = el.get('userInfo') or {}
                if isinstance(ui, dict):
                    for f in ACTION_TEXT_FIELDS[act]:
                        if f in ui and isinstance(ui[f], str):
                            add(ui[f], lineno, f'action.{act}.{f}')
        for k, v in el.items():
            if k in ('initial','linkPath','divert','func','get','var','name','buildingBlock','condition','params','action','userInfo','set','doFuncs'):
                continue
            walk(v, lineno, path + '/' + k)

for a, b in RANGES:
    for i in range(a, min(b, len(lines))):
        ln = lines[i]
        if not ln.strip():
            continue
        walk(json.loads(ln), i)

print('unique:', len(entries))
print('occurrences:', sum(e['n'] for e in entries.values()))

# 保存待翻译
os.makedirs(r'D:\git\project\80 days CN\translation', exist_ok=True)
out = [{'en': k, 'n': v['n'], 'ctx': v['ctx'], 'zh': ''} for k, v in entries.items()]
json.dump(out, open(r'D:\git\project\80 days CN\translation\opening_todo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved opening_todo.json  items=', len(out))

# 统计片段 vs 句子
frags = [o for o in out if len(o['en']) < 25]
sents = [o for o in out if len(o['en']) >= 25]
print('短片段(<25 chars):', len(frags), ' 长句(>=25):', len(sents))
print('片段示例:', [o['en'] for o in frags[:15]])
