import UnityPy, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = r'F:\Games\80 Days\80 Days_Data'
env = UnityPy.load(base)

outdir = r'D:\git\project\80 days CN\extracted\fonts'
os.makedirs(outdir, exist_ok=True)

for obj in env.objects:
    if obj.type.name == 'Font':
        try:
            d = obj.read()
            print(f'=== Font: {d.m_Name}  (assets: {obj.assets_file.name}) ===')
            print('  m_AsciiStartOffset:', getattr(d, 'm_AsciiStartOffset', None))
            print('  m_Ascent:', getattr(d, 'm_Ascent', None))
            print('  m_Descent:', getattr(d, 'm_Descent', None))
            print('  m_LineSpacing:', getattr(d, 'm_LineSpacing', None))
            print('  m_DefaultMaterial:', getattr(d, 'm_DefaultMaterial', None))
            print('  m_FontData (bytes):', len(d.m_FontData) if d.m_FontData else 0)
            if d.m_FontData and len(d.m_FontData) > 1000:
                p = os.path.join(outdir, f'{d.m_Name}.ttf')
                with open(p, 'wb') as f:
                    f.write(d.m_FontData)
                print('  -> saved TTF to', p)
            elif d.m_FontData:
                print('  fontdata head:', bytes(d.m_FontData[:32]))
        except Exception as e:
            print('ERR font', repr(e))

# Check for TextMeshPro font assets (as MonoBehaviour or via type)
print('\n=== Search for TMP font asset objects ===')
n = 0
for obj in env.objects:
    tn = obj.type.name
    if 'Font' in tn or 'TMP' in tn or 'SDF' in tn:
        print(f'  {tn} in {obj.assets_file.name}')
        n += 1
print('TMP-ish types:', n)
