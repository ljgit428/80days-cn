import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ex = r'D:\git\project\80 days CN\extracted'

for name in ['chaptertitles', 'facts', 'itemsdata', 'cast', '80days', 'audioscapes', 'assetdata', 'mapdata', 'routedata', 'placements']:
    p = os.path.join(ex, name)
    try:
        raw = open(p, 'r', encoding='utf-8').read()
    except Exception as e:
        print(f'### {name}: read error {e}')
        continue
    print(f'\n######## {name}  ({len(raw)} chars) ########')
    try:
        d = json.loads(raw)
        print('  top type:', type(d).__name__)
        if isinstance(d, dict):
            ks = list(d.keys())
            print('  keys (first 20):', ks[:20])
        elif isinstance(d, list):
            print('  list len:', len(d), 'first:', json.dumps(d[:2], ensure_ascii=False)[:300])
    except Exception as e:
        print('  not valid single JSON:', e)
        print('  head:', repr(raw[:200]))
