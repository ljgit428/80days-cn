import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ex = r'D:\git\project\80 days CN\extracted'

# chaptertitles
d = json.load(open(os.path.join(ex, 'chaptertitles'), encoding='utf-8'))
print('=== chaptertitles ===')
for t in d['titles'][:5]:
    print(' ', t)

# facts
d = json.load(open(os.path.join(ex, 'facts'), encoding='utf-8'))
print('\n=== facts (London) ===')
print(json.dumps(d['London'][:2], ensure_ascii=False, indent=1))

# itemsdata
d = json.load(open(os.path.join(ex, 'itemsdata'), encoding='utf-8'))
print('\n=== itemsdata structure ===')
print('icons keys:', list(d['icons'].keys()))
print('sets sample:', json.dumps(d['sets'], ensure_ascii=False)[:300])
items = d['items']
print('items type:', type(items).__name__)
if isinstance(items, dict):
    ks = list(items.keys())
    print('items count:', len(ks))
    k0 = ks[0]
    print('sample item', k0, ':', json.dumps(items[k0], ensure_ascii=False)[:600])
elif isinstance(items, list):
    print('items count:', len(items))
    print('sample:', json.dumps(items[0], ensure_ascii=False)[:600])

# cast
d = json.load(open(os.path.join(ex, 'cast'), encoding='utf-8'))
print('\n=== cast ===')
print('tags:', json.dumps(d['tags'], ensure_ascii=False)[:300])
cast = d['cast']
print('cast type:', type(cast).__name__, 'count:', len(cast))
if isinstance(cast, dict):
    k0 = list(cast.keys())[0]
    print('sample cast', k0, ':', json.dumps(cast[k0], ensure_ascii=False)[:500])
elif isinstance(cast, list):
    print('sample:', json.dumps(cast[0], ensure_ascii=False)[:500])

# mapdata cities
d = json.load(open(os.path.join(ex, 'mapdata'), encoding='utf-8'))
print('\n=== mapdata ===')
cities = d['cities']
print('cities type:', type(cities).__name__, 'count:', len(cities))
if isinstance(cities, dict):
    k0 = list(cities.keys())[0]
    print('sample city', k0, ':', json.dumps(cities[k0], ensure_ascii=False)[:800])
elif isinstance(cities, list):
    print('sample:', json.dumps(cities[0], ensure_ascii=False)[:800])
print('\njourneys type:', type(d['journeys']).__name__, 'count:', len(d['journeys']))
