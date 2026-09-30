import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = r'F:\Games\80 Days\80 Days_Data\Managed\Assembly-CSharp.dll'
data = open(p, 'rb').read()
print('dll size:', len(data))

# extract printable ASCII strings >= 6 chars
strings = re.findall(rb'[\x20-\x7e]{6,300}', data)
print('raw strings:', len(strings))

# filter to likely UI/prose strings
interesting = []
for s in strings:
    t = s.decode('ascii')
    if re.search(r'[A-Za-z]{3,}', t):
        interesting.append(t)

print('interesting:', len(interesting))

# heuristics: sentences with spaces (prose-like) or UI words
ui_words = ['Continue','New Game','Load','Save','Settings','Options','Quit','Exit','Back','Apply',
            'Resume','Start','Chapter','Credits','Language','Sound','Music','Volume','Are you sure',
            'Yes','No','Cancel','OK','Days','Day','Week','Market','Hotel','Depart','Explore','Journey',
            'Inventory','Map','Travel','Arrived','Departed','Fogg','Passepartout']
seen = set()
ui_hits = []
for t in interesting:
    for w in ui_words:
        if w in t and t not in seen:
            seen.add(t)
            ui_hits.append(t)
            break

print('\n=== UI-ish strings (first 150) ===')
for t in ui_hits[:150]:
    print('  ', repr(t))
