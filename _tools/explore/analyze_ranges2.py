import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days'
d = json.load(open(p, encoding='utf-8'))
ranges = d['indexed-content']['ranges']

# ranges: name -> "startLine endLine" (空格分隔)。每行一个 json value
print('ranges 总数:', len(ranges))

# inkcontent 的行号是 0-based 还是 1-based？ranges['storycrashed'] = "0 150"
# 先确认行数 = 2574，ranges 数量也是 2574 -> 一一对应？不一定，ranges 是命名区间
items = list(ranges.items())
# 检查区间是否有重叠/连续
starts = []
for name, v in items:
    parts = str(v).split()
    s, e = int(parts[0]), int(parts[1])
    starts.append((s, e, name))

starts.sort()
print('前 20 个区间:')
for s, e, n in starts[:20]:
    print(f'  {s:5d}-{e:5d} {n}')

# inkcontent 行数
raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
lines = raw.split('\n')
nlines = len([l for l in lines if l.strip()])
print('\ninkcontent 非空行数:', nlines)

# 找 intro/london/paris 相关键
keys = ['intro', 'london', 'paris', 'meet_manager', 'begging', 'leave_london', 'to_paris', 'train', 'channel']
print('\n相关区间:')
for s, e, n in starts:
    nl = n.lower()
    if any(k in nl for k in keys):
        print(f'  {s:5d}-{e:5d} {n}')
