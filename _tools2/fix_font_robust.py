# -*- coding: utf-8 -*-
"""
80 Days 汉化：缺字问题修复 + 诊断开关
用法: python _tools2\fix_font_robust.py

做三件事（都会先备份到 ORIGINAL_BACKUP\before_font_robust\）：
 1. TMP Settings: m_warningsDisabled 1 -> 0
    让 TextMeshPro 把「某字找不到、已替换为空格」写进 output_log.txt。
    这是唯一能确定运行时真实失败原因的手段（当前被关掉了，所以日志里什么都没有）。
 2. TMP Settings: m_fallbackFontAssets 补上中文动态后备（当前是空列表）。
    这样任何没有单独配后备的文字对象也能显示中文。
 3. LiberationSans SDF（TMP 默认字体，当前 fallback 为空）挂上同一个中文后备。

注：TMP Settings 在 resources.assets 里，它的外部引用 FileID 2 = sharedassets0.assets，
    所以引用 sharedassets0 的 pathID 35（Lato-Medium SDF Dynamic Fallback）。
"""
import os, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r'F:\Games\80 Days'
D    = os.path.join(GAME, '80 Days_Data')
ROOT = r'D:\git\project\80 days CN'
BK   = os.path.join(ROOT, 'ORIGINAL_BACKUP', 'before_font_robust')
OUT  = os.path.join(ROOT, 'patched')
os.makedirs(BK, exist_ok=True); os.makedirs(OUT, exist_ok=True)

CJK_FALLBACK = {'m_FileID': 2, 'm_PathID': 35}   # sharedassets0.assets / Lato-Medium SDF Dynamic Fallback

gen = TypeTreeGenerator('2018.4.30f1'); gen.load_local_game(GAME)

fn  = 'resources.assets'
src = os.path.join(D, fn)
if not os.path.exists(os.path.join(BK, fn)):
    shutil.copy(src, os.path.join(BK, fn)); print('backed up ->', os.path.join(BK, fn))

env = UnityPy.load(src); env.typetree_generator = gen
objs = {o.path_id: o for o in env.objects}
changed = 0

# --- 1 & 2: TMP Settings ---
for pid, o in objs.items():
    if o.type.name != 'MonoBehaviour': continue
    try: t = o.read_typetree()
    except Exception: continue
    if 'm_warningsDisabled' not in t: continue
    print('TMP Settings pathID=%s' % pid)
    print('   warningsDisabled  %s -> 0' % t.get('m_warningsDisabled'))
    t['m_warningsDisabled'] = 0
    fb = list(t.get('m_fallbackFontAssets') or [])
    if not any(x.get('m_PathID') == 35 for x in fb):
        fb.append(CJK_FALLBACK)
        print('   fallbackFontAssets [] -> %s' % fb)
    t['m_fallbackFontAssets'] = fb
    o.save_typetree(t); changed += 1
    break

# --- 3: LiberationSans SDF ---
for pid, o in objs.items():
    if o.type.name != 'MonoBehaviour': continue
    try: t = o.read_typetree()
    except Exception: continue
    if t.get('m_Name') != 'LiberationSans SDF': continue
    fb = list(t.get('m_FallbackFontAssetTable') or [])
    if not any(x.get('m_PathID') == 35 for x in fb):
        fb.append(CJK_FALLBACK)
        t['m_FallbackFontAssetTable'] = fb
        o.save_typetree(t); changed += 1
        print('LiberationSans SDF (pathID %s) fallback -> %s' % (pid, fb))
    break

if not changed:
    print('nothing changed'); raise SystemExit(1)

out = os.path.join(OUT, fn)
open(out, 'wb').write(env.file.save())
del env, objs
import gc; gc.collect()
shutil.copy(out, src)
print('installed', src, os.path.getsize(src))

# --- 校验 ---
env = UnityPy.load(src); env.typetree_generator = gen
for o in env.objects:
    if o.type.name != 'MonoBehaviour': continue
    try: t = o.read_typetree()
    except Exception: continue
    if 'm_warningsDisabled' in t:
        print('VERIFY warningsDisabled =', t['m_warningsDisabled'], ' fallback =', t.get('m_fallbackFontAssets'))
    if t.get('m_Name') == 'LiberationSans SDF':
        print('VERIFY LiberationSans fallback =', t.get('m_FallbackFontAssetTable'))
