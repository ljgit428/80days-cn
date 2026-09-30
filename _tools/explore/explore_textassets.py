import UnityPy
import os, sys

base = r'F:\Games\80 Days\80 Days_Data'
env = UnityPy.load(base)

for obj in env.objects:
    if obj.type.name == 'TextAsset':
        try:
            data = obj.read()
            script = data.m_Script
            if isinstance(script, str):
                size = len(script.encode('utf-8', errors='replace'))
                preview = script[:120].replace('\n', '\\n')
            else:
                size = len(script)
                preview = str(script[:120])
            print(f'[{obj.assets_file.name}] {data.m_Name}  bytes={size}')
            print(f'    preview: {preview}')
        except Exception as e:
            print('ERR', repr(e))
