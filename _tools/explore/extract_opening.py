import sys, io, json, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
lines = raw.split('\n')

# 开头段落范围：伦敦 intro/银行/begging/prologue/london_main + 巴黎火车 + 巴黎首到
RANGES = [(0, 31), (785, 801), (1174, 1177)]

MARKUP = re.compile(r'^(\s|<[^>]+>|[A-Za-z_][A-Za-z0-9_]*|[\d\.,;:\-\(\)"\'\£\!\?\…]*)*$')

def is_translatable(s):
    if not s.strip():
        return False
    # 纯标记/标识符/数字符号
    if MARKUP.fullmatch(s):
        # 但含字母的单词可能仍是可译的（如 "playing whist"）
        # MARKUP 允许单个标识符，所以 "whist" 会被判为不可译。修正：含2个以上字母且像单词的保留
        return False
    return bool(re.search(r'[A-Za-z]', s))

# 更宽松：凡是含字母且不是纯标识符/标记的都收
WORD_RE = re.compile(r'[A-Za-z]')

def classify(s):
    if not s.strip():
        return False
    if not WORD_RE.search(s):
        return False
    # 去掉所有标记后是否还有字母内容
    stripped = re.sub(r'<[^>]+>', '', s).strip()
    if not stripped:
        return False
    # 纯单个标识符（无空格、无标点）——可能是单词片段，仍需翻译（如 dispirited）
    return True

# 提取所有字符串节点（保留来源行号和结构路径，便于上下文）
entries = {}   # en -> {count, contexts:[(line, path)]}

CTX_KEYS = ('then','otherwise','cycle','sequence','onceonly','shuffle','pairs','option','content')

def walk(el, path, lineno):
    if isinstance(el, str):
        if classify(el):
            key = el
            if key not in entries:
                entries[key] = {'count': 0, 'ctx': []}
            entries[key]['count'] += 1
            if len(entries[key]['ctx']) < 3:
                entries[key]['ctx'].append((lineno, path[-3:]))
    elif isinstance(el, list):
        for x in el:
            walk(x, path, lineno)
    elif isinstance(el, dict):
        for k, v in el.items():
            if k in ('initial','linkPath','divert','func','get','var','name','buildingBlock','condition','params','action','userInfo','set','doFuncs'):
                continue
            walk(v, path + [k], lineno)

for a, b in RANGES:
    for i in range(a, min(b, len(lines))):
        ln = lines[i]
        if not ln.strip():
            continue
        d = json.loads(ln)
        walk(d, [], i)

print('unique translatable strings in opening:', len(entries))
total = sum(e['count'] for e in entries.values())
print('total occurrences:', total)
chars = sum(len(k) * e['count'] for k, e in entries.items())
print('total chars (with repeats):', chars)

# 按字符数排序，长的先
srt = sorted(entries.items(), key=lambda kv: -len(kv[0]) * kv[1]['count'])
print('\n=== 最长的 30 条 ===')
for k, e in srt[:30]:
    print(f'  ({e["count"]}x, ctx {e["ctx"][0]}) {k[:110]!r}')

os.makedirs(r'D:\git\project\80 days CN\translation', exist_ok=True)
out = {k: {'count': v['count'], 'ctx': v['ctx'], 'zh': ''} for k, v in entries.items()}
json.dump(out, open(r'D:\git\project\80 days CN\translation\opening_todo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nsaved -> translation/opening_todo.json')
