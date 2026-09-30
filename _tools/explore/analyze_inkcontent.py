import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days.inkcontent'
raw = open(p, 'r', encoding='utf-8').read()
print('length chars:', len(raw))

data = json.loads(raw)
print('top-level type:', type(data).__name__, 'len:', len(data))

# inspect first 5 elements
for i, el in enumerate(data[:5]):
    print(f'--- element {i} ---')
    print('  type:', type(el).__name__)
    s = json.dumps(el, ensure_ascii=False)
    print('  ', s[:400])

# count element types
from collections import Counter
c = Counter(type(el).__name__ for el in data)
print('\nelement types:', c)
