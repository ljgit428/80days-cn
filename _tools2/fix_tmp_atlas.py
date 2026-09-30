# 扩大 TMP 动态后备字体的图集（512->4096），并给无后备的静态 TMP 字体挂上中文动态后备
import UnityPy, os, shutil, sys
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
GAME = r'F:\Games\80 Days'; D = GAME + r'\80 Days_Data'
BK = r'D:\git\project\80 days CN\ORIGINAL_BACKUP\before_tmp_fix'
os.makedirs(BK, exist_ok=True)
SIZE = 4096
gen = TypeTreeGenerator('2018.4.30f1'); gen.load_local_game(GAME)
plan = {   # 文件 -> (动态后备字体 pathID, 贴图 pathID, 需要挂后备的静态字体 pathID 列表)
    'sharedassets0.assets': (35, 17, []),
    'sharedassets1.assets': (995, 162, [997, 998]),
}
for fn, (dyn, tex_id, statics) in plan.items():
    src = os.path.join(D, fn)
    if not os.path.exists(os.path.join(BK, fn)): shutil.copy(src, os.path.join(BK, fn))
    env = UnityPy.load(src); env.typetree_generator = gen
    objs = {o.path_id: o for o in env.objects}
    t = objs[dyn].read_typetree()
    t['m_AtlasWidth'] = SIZE; t['m_AtlasHeight'] = SIZE
    t['m_GlyphTable'] = []; t['m_CharacterTable'] = []; t['m_UsedGlyphRects'] = []
    t['m_FreeGlyphRects'] = [{'m_X': 0, 'm_Y': 0, 'm_Width': SIZE - 1, 'm_Height': SIZE - 1}]
    objs[dyn].save_typetree(t)
    tex = objs[tex_id].read()
    print(fn, 'tex before', tex.m_Name, tex.m_Width, tex.m_Height, tex.m_TextureFormat, 'readable', getattr(tex, 'm_IsReadable', None), 'mips', getattr(tex, 'm_MipCount', None))
    tt = objs[tex_id].read_typetree()
    tt['m_Width'] = SIZE; tt['m_Height'] = SIZE
    tt['m_CompleteImageSize'] = SIZE * SIZE
    tt['image data'] = bytes(SIZE * SIZE)
    if 'm_StreamData' in tt: tt['m_StreamData'] = {'offset': 0, 'size': 0, 'path': ''}
    if 'm_MipCount' in tt: tt['m_MipCount'] = 1
    objs[tex_id].save_typetree(tt)
    for sid in statics:
        s = objs[sid].read_typetree()
        s['m_FallbackFontAssetTable'] = list(s.get('m_FallbackFontAssetTable') or []) + [{'m_FileID': 0, 'm_PathID': dyn}]
        objs[sid].save_typetree(s)
        print('fallback added', s['m_Name'])
    out = os.path.join(r'D:\git\project\80 days CN\patched', fn)
    open(out, 'wb').write(env.file.save())
    data=None; del env, objs; import gc; gc.collect()
    shutil.copy(out, src)
    print('installed', fn, os.path.getsize(src))
# 校验
for fn, (dyn, tex_id, statics) in plan.items():
    env = UnityPy.load(os.path.join(D, fn)); env.typetree_generator = gen
    objs = {o.path_id: o for o in env.objects}
    t = objs[dyn].read_typetree(); x = objs[tex_id].read()
    print('verify', fn, t['m_Name'], t['m_AtlasWidth'], t['m_AtlasHeight'], x.m_Width, x.m_Height, len(x.get_image_data() if hasattr(x,'get_image_data') else b'') if False else '')
