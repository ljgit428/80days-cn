from fontTools import varLib
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib import TTFont
import os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

src = r'C:\Windows\Fonts\NotoSansSC-VF.ttf'
outdir = r'D:\git\project\80 days CN\extracted\fonts\cn'
os.makedirs(outdir, exist_ok=True)

# 权重映射：Lato -> Noto Sans SC
plan = [
    ('Lato-Thin',        100),   # Thin
    ('Lato-Light',       300),   # Light
    ('Lato-LightItalic', 300),   # Light (italic 由 Unity 伪斜体处理)
    ('Lato-Medium',      500),   # Medium
]

for lato_name, wght in plan:
    out = os.path.join(outdir, lato_name + '.NotoSC.ttf')
    if os.path.exists(out):
        print('skip exists:', out)
        continue
    f = TTFont(src, fontNumber=0)
    inst = instantiateVariableFont(f, {'wght': wght})
    # 清理 STAT 表里的轴信息（静态字体不需要）
    for t in ('STAT','fvar','avar','HVAR','gvar','VVAR'):
        if t in inst:
            del inst[t]
    # 修正 name 表
    try:
        name = inst['name']
        for rid in (1, 4, 6):
            for rec in name.names:
                if rec.nameID == rid:
                    rec.string = lato_name.encode(rec.getEncoding())
    except Exception as e:
        print('name fix err', e)
    inst.save(out)
    print('saved:', out, os.path.getsize(out), 'bytes')
