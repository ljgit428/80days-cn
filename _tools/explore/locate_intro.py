import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days.inkcontent'
raw = open(p, 'r', encoding='utf-8').read()
lines = raw.split('\n')

# 统计每行的 stitch 名和 BuildingBlock，定位开头
print('=== 前 40 行的轮廓 ===')
for i, ln in enumerate(lines[:40]):
    if not ln.strip():
        continue
    d = json.loads(ln)
    tag = ''
    if isinstance(d, dict) and 'stitches' in d:
        tag = 'CONTAINER initial=' + str(d.get('initial')) + ' stitches=' + str(list(d['stitches'].keys())[:6])
    elif isinstance(d, list):
        bbs = []
        divs = []
        for el in d:
            if isinstance(el, dict):
                if 'buildingBlock' in el:
                    bbs.append(el['buildingBlock'])
                if 'divert' in el:
                    divs.append(el['divert'])
        txts = [e for e in d if isinstance(e, str)][:3]
        tag = f'FLOW bb={bbs[:4]} divert={divs[:4]} text={txts}'
    print(f'{i:4d}: {tag[:180]}')
