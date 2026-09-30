import UnityPy
import os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = r'F:\Games\80 Days\80 Days_Data'
out = r'D:\git\project\80 days CN\extracted'
os.makedirs(out, exist_ok=True)

env = UnityPy.load(base)

for obj in env.objects:
    if obj.type.name == 'TextAsset':
        try:
            data = obj.read()
            name = data.m_Name
            script = data.m_Script
            if isinstance(script, str):
                raw = script.encode('utf-8', errors='surrogateescape')
            else:
                raw = script
            p = os.path.join(out, name)
            with open(p, 'wb') as f:
                f.write(raw)
            print(f'[{obj.assets_file.name}] {name}  bytes={len(raw)}  -> {p}')
        except Exception as e:
            print('ERR', name, repr(e))

# also dump fonts info
print('\n--- Fonts ---')
for obj in env.objects:
    if obj.type.name == 'Font':
        try:
            data = obj.read()
            print(f'{data.m_Name}  assets={obj.assets_file.name}')
        except Exception as e:
            print('ERR font', repr(e))
