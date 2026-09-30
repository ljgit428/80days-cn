import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days.inkcontent'
raw = open(p, 'r', encoding='utf-8').read()
lines = raw.split('\n')

def collect_text(el, out):
    """递归收集可翻译字符串，以及 BuildingBlock 引用"""
    if isinstance(el, str):
        out['texts'].append(el)
    elif isinstance(el, list):
        for x in el:
            collect_text(x, out)
    elif isinstance(el, dict):
        for k, v in el.items():
            if k in ('initial','linkPath','divert','func','get','var','name','buildingBlock'):
                if k == 'buildingBlock':
                    out['bbs'].add(v)
                continue
            if k == 'params':
                # params 里 condition 参数可能是数字或 get var；但 option 的 params 不是
                continue
            collect_text(v, out)

# 找巴黎相关：paris
paris_lines = []
for i, ln in enumerate(lines):
    if not ln.strip():
        continue
    if 'paris' in ln.lower():
        paris_lines.append(i)

print('行内含 paris 的行号（前 40 个）:', paris_lines[:40])
print('总数:', len(paris_lines))

# 看第 1 行（intro）完整内容
d = json.loads(lines[1])
print('\n=== 行 1 (intro 容器) 全文 ===')
print(json.dumps(d, ensure_ascii=False, indent=1)[:4000])
