import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days'
d = json.load(open(p, encoding='utf-8'))

print('top keys:', list(d.keys()))
bbs = d.get('buildingBlocks')
print('buildingBlocks type:', type(bbs).__name__)
if isinstance(bbs, dict):
    ks = list(bbs.keys())
    print('bb count:', len(ks))
    print('first 10 bb names:', ks[:10])
    k0 = ks[0]
    print('sample bb', k0, ':', json.dumps(bbs[k0], ensure_ascii=False)[:500])
elif isinstance(bbs, list):
    print('bb count:', len(bbs))
    print('first 3:', json.dumps(bbs[:3], ensure_ascii=False)[:800])

# indexed-content
ic = d.get('indexed-content')
print('\nindexed-content type:', type(ic).__name__)
if isinstance(ic, dict):
    ks = list(ic.keys())
    print('ic count:', len(ks), 'first:', ks[:10])
    k0 = ks[0]
    print('sample ic', k0, ':', json.dumps(ic[k0], ensure_ascii=False)[:400])
elif isinstance(ic, list):
    print('ic count:', len(ic))
    print('first 2:', json.dumps(ic[:2], ensure_ascii=False)[:600])

# variables
v = d.get('variables')
print('\nvariables count:', len(v) if v else 0)
if v:
    ks = list(v.keys())[:15]
    print('var keys sample:', ks)
