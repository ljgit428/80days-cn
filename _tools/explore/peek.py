import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'D:\git\project\80 days CN\extracted\80days.inkcontent'
raw = open(p, 'r', encoding='utf-8').read()
print('=== first 2000 chars ===')
print(repr(raw[:2000]))
print()
print('=== chars 140-400 ===')
print(repr(raw[140:400]))
