import UnityPy, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = r'F:\Games\80 Days\80 Days_Data'
env = UnityPy.load(base)

outdir = r'D:\git\project\80 days CN\extracted\fonts'
os.makedirs(outdir, exist_ok=True)

fonts = {}
for obj in env.objects:
    if obj.type.name == 'Font':
        d = obj.read()
        fonts[d.m_Name] = (obj, d)

for name, (obj, d) in fonts.items():
    print(f'=== {name} ===')
    # character rects
    try:
        cr = d.m_CharacterRects
        print('  m_CharacterRects count:', len(cr) if cr else 0)
    except Exception as e:
        print('  m_CharacterRects err:', e)
    try:
        print('  m_Texture:', d.m_Texture)
    except Exception as e:
        print('  m_Texture err:', e)
    # save fontdata
    fd = d.m_FontData
    if fd:
        data = bytes(bytearray(fd)) if isinstance(fd, list) else bytes(fd)
        print('  fontdata len:', len(data), 'magic:', data[:8].hex())
        p = os.path.join(outdir, name + '.ttf')
        with open(p, 'wb') as f:
            f.write(data)
        print('  ->', p)
    # check material shader
    try:
        mat = d.m_DefaultMaterial.read()
        sh = mat.m_Shader.read() if mat.m_Shader and mat.m_Shader.data else None
        print('  material:', mat.m_Name, 'shader:', sh.m_ParsedForm.m_Name if sh else None)
    except Exception as e:
        print('  material err:', repr(e)[:120])
