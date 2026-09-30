import UnityPy, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
把 sharedassets0.assets 里 4 个 Lato 动态字体的 TTF 数据替换为 Noto Sans SC 静态实例。
"""
src = r'F:\Games\80 Days\80 Days_Data\sharedassets0.assets'
fdir = r'D:\git\project\80 days CN\extracted\fonts\cn'

mapping = {
    'Lato-Thin':        os.path.join(fdir, 'Lato-Thin.NotoSC.ttf'),
    'Lato-Light':       os.path.join(fdir, 'Lato-Light.NotoSC.ttf'),
    'Lato-LightItalic': os.path.join(fdir, 'Lato-LightItalic.NotoSC.ttf'),
    'Lato-Medium':      os.path.join(fdir, 'Lato-Medium.NotoSC.ttf'),
}

env = UnityPy.load(src)
patched = []
for obj in env.objects:
    if obj.type.name != 'Font':
        continue
    d = obj.read()
    if d.m_Name not in mapping:
        continue
    ttf = open(mapping[d.m_Name], 'rb').read()
    # m_FontData 原本是 list[int]
    d.m_FontData = list(ttf)
    d.save()          # UnityPy 1.25: 在实例上调 save()
    patched.append((d.m_Name, len(ttf)))
    print(f'patched {d.m_Name}: {len(ttf)} bytes')

print('patched count:', len(patched))
out_dir = r'D:\git\project\80 days CN\patched'
os.makedirs(out_dir, exist_ok=True)
env.save(out_path=out_dir)
import shutil
shutil.copy(os.path.join(out_dir, 'sharedassets0.assets'), src)
print('written to', src)
print('new file size:', os.path.getsize(src))
