import UnityPy, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = r'F:\Games\80 Days\80 Days_Data'
env = UnityPy.load(base)

# Check GameObjects and their components
from collections import Counter
comp_counter = Counter()
go_sample = None
for obj in env.objects:
    if obj.type.name == 'GameObject':
        try:
            d = obj.read()
            comps = [(c.data.type.name if c.data else '?') for c in d.m_Components]
            for c in comps:
                comp_counter[c] += 1
            if go_sample is None and any(c in ('Text','Button','Image','RectTransform') for c in comps):
                go_sample = (d.m_Name, comps)
        except Exception as e:
            pass

print('=== component types on GameObjects ===')
for k, v in comp_counter.most_common(30):
    print(f'  {k}: {v}')

if go_sample:
    print('\nsample GO with UI:', go_sample[0], go_sample[1])

# Try to find Text components specifically
print('\n=== Searching for Text components ===')
n = 0
for obj in env.objects:
    try:
        if obj.type.name == 'Text':
            d = obj.read()
            print(f'  Text: {d.m_Text[:100]!r} font={d.m_Font.data.m_Name if d.m_Font and d.m_Font.data else None}')
            n += 1
            if n > 40: break
    except Exception as e:
        pass
print('Text components found (shown):', n)
