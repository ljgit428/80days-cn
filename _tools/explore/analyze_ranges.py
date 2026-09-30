import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days'
d = json.load(open(p, encoding='utf-8'))

ic = d['indexed-content']
print('indexed-content keys:', list(ic.keys()))
print('filename:', ic['filename'])
ranges = ic['ranges']
print('ranges type:', type(ranges).__name__, 'count:', len(ranges) if ranges else 0)
if isinstance(ranges, dict):
    ks = list(ranges.keys())
    print('range keys sample:', ks[:10])
    k0 = ks[0]
    print('sample range', k0, ':', json.dumps(ranges[k0], ensure_ascii=False)[:600])
elif isinstance(ranges, list):
    print('first 3:', json.dumps(ranges[:3], ensure_ascii=False)[:800])

# 看 buildingBlocks 里和伦敦/巴黎开头的项
bbs = d['buildingBlocks']
for k in list(bbs.keys()):
    kl = k.lower()
    if kl.startswith('intro') or 'london' in kl or kl.startswith('paris') or kl.startswith('begin') or kl.startswith('start'):
        print(f'\nBB {k}: {json.dumps(bbs[k], ensure_ascii=False)[:300]}')
