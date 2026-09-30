import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
lines = raw.split('\n')

def flatten(el, depth=0):
    """把 content 结构压成可读文本，标记结构"""
    out = []
    if isinstance(el, str):
        out.append(el)
    elif isinstance(el, list):
        for x in el:
            out.extend(flatten(x, depth))
    elif isinstance(el, dict):
        for k, v in el.items():
            if k in ('then','otherwise'):
                out.append(f'[{k}:')
                out.extend(flatten(v, depth))
                out.append(']')
            elif k in ('cycle','sequence','onceonly','shuffle','pairs'):
                out.append(f'[{k}:')
                out.extend(flatten(v, depth))
                out.append(']')
            elif k == 'option':
                out.append('<OPT>')
                out.extend(flatten(v, depth))
                out.append('</OPT>')
            elif k in ('divert','buildingBlock','condition','func','params','get','var','linkPath','initial','name'):
                pass
    return out

def line_desc(d):
    parts = []
    if isinstance(d, dict) and 'stitches' in d:
        parts.append('CONTAINER initial=' + str(d.get('initial')) + ' stitches=' + str(list(d['stitches'].keys())))
        for sn, sv in d['stitches'].items():
            txt = ''.join(flatten(sv.get('content', [])))
            parts.append(f'   stitch [{sn}]: {txt[:200]}')
    elif isinstance(d, list):
        txt = ''.join(flatten(d))
        parts.append('FLOW: ' + txt[:250])
    return '\n'.join(parts)

# 开头候选行
for rng in [(0, 30), (785, 812), (1174, 1182)]:
    a, b = rng
    print(f'\n############ 行 {a}-{b} ############')
    for i in range(a, min(b, len(lines))):
        ln = lines[i]
        if not ln.strip():
            continue
        try:
            d = json.loads(ln)
        except Exception as e:
            print(f'{i}: PARSE ERR {e}')
            continue
        print(f'--- 行 {i} ---')
        print(line_desc(d))
