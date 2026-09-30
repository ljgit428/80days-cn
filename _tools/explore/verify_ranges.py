import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

raw = open(r'D:\git\project\80 days CN\extracted\80days.inkcontent', encoding='utf-8').read()
d = json.load(open(r'D:\git\project\80 days CN\extracted\80days', encoding='utf-8'))
ranges = d['indexed-content']['ranges']

def show(name):
    if name not in ranges:
        print(f'{name}: NOT FOUND')
        return
    s, ln = map(int, str(ranges[name]).split())
    seg = raw[s:s+ln]
    print(f'=== {name}  offset={s} len={ln} ===')
    print(repr(seg[:400]))
    print()

for n in ['prologue','london','paris_first_time','paris_train_departure_first_time','paris_train1','meet_manager','begging_hub','london_main','paris_night']:
    show(n)

# 计算字符偏移 -> 行号 的映射
line_offsets = []
acc = 0
for i, l in enumerate(raw.split('\n')):
    line_offsets.append(acc)
    acc += len(l) + 1  # +1 for newline

def offset_to_line(off):
    import bisect
    idx = bisect.bisect_right(line_offsets, off) - 1
    return idx

print('=== 偏移转行号 ===')
for n in ['prologue','london','paris_first_time','paris_train_departure_first_time','paris_train1','meet_manager','begging_hub','london_main','paris_night','paris_not_first']:
    s, ln = map(int, str(ranges[n]).split())
    print(f'{n}: line {offset_to_line(s)} .. line {offset_to_line(s+ln-1)}')
