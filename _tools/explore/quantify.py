import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days.inkcontent'
raw = open(p, 'r', encoding='utf-8').read()
lines = raw.split('\n')
# check trailing
print('total lines:', len(lines))
print('last line empty?', repr(lines[-1][:50]) if lines[-1] else 'EMPTY')

ok = 0
bad = 0
kinds = {}
for i, ln in enumerate(lines):
    if not ln.strip():
        continue
    try:
        d = json.loads(ln)
        ok += 1
        if isinstance(d, list):
            kinds['flow_array'] = kinds.get('flow_array', 0) + 1
        elif isinstance(d, dict):
            if 'stitches' in d:
                kinds['story_container'] = kinds.get('story_container', 0) + 1
            else:
                kinds['dict_other'] = kinds.get('dict_other', 0) + 1
        else:
            kinds['scalar'] = kinds.get('scalar', 0) + 1
    except Exception as e:
        bad += 1
        if bad < 5:
            print('BAD line', i, repr(ln[:120]), e)

print('parsed ok:', ok, 'bad:', bad)
print('kinds:', kinds)

# Count translatable strings via a recursive walk
strings = []
def walk(el):
    if isinstance(el, str):
        strings.append(el)
    elif isinstance(el, list):
        for x in el:
            walk(x)
    elif isinstance(el, dict):
        for k, v in el.items():
            # keys that hold translatable text
            if k in ('option',):
                walk(v)
            elif k in ('then', 'otherwise'):
                walk(v)
            elif k in ('cycle', 'sequence', 'onceonly', 'shuffle', 'pairs'):
                # these are lists of lists
                walk(v)
            elif k == 'content':
                walk(v)
            elif k == 'stitches':
                # dict of stitchname -> {content: [...]}
                for sn, sv in v.items():
                    walk(sv)
            elif k == 'initial':
                pass  # identifier
            else:
                # generic: only walk into known content-bearing? be conservative
                if k in ('linkPath','divert','condition','func','params','buildingBlock','var','get','set','to','name','tags'):
                    pass
                else:
                    walk(v)

for ln in lines:
    if not ln.strip():
        continue
    d = json.loads(ln)
    walk(d)

print('\ntotal raw string nodes:', len(strings))
# filter out pure markup / identifiers / numbers
import re
def is_translatable(s):
    if not s.strip():
        return False
    # pure punctuation/markup like <br>, tags
    if re.fullmatch(r'(<[^>]+>|\s|[\d\.,;:\-\(\)"\']*|[A-Za-z_][A-Za-z0-9_\.]*)', s):
        return False
    # contains at least one letter that isn't just markup
    return bool(re.search(r'[A-Za-z]', s))

trans = [s for s in strings if is_translatable(s)]
print('translatable (heuristic):', len(trans))
total_chars = sum(len(s) for s in trans)
print('total chars in translatable strings:', total_chars)
uniq = sorted(set(trans))
print('unique translatable strings:', len(uniq))
print('unique total chars:', sum(len(s) for s in uniq))
