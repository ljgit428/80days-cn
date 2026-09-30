import UnityPy, os, glob, json
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
d=r'F:\Games\80 Days\80 Days_Data'
gen=TypeTreeGenerator('2018.4.30f1'); gen.load_local_game(r'F:\Games\80 Days')
for f in sorted(glob.glob(d+r'\*.assets')):
    env=UnityPy.load(f); env.typetree_generator=gen
    for o in env.objects:
        if o.type.name!='MonoBehaviour': continue
        try:
            t=o.read_typetree()
        except Exception as e: continue
        if 'm_AtlasPopulationMode' in t or 'm_fontInfo' in t or 'm_FaceInfo' in t and 'm_GlyphTable' in t:
            fi=t.get('m_FaceInfo',{})
            print(os.path.basename(f), o.path_id, t.get('m_Name'), 'ver',t.get('m_Version'),'mode',t.get('m_AtlasPopulationMode'),
                  'atlas',t.get('m_AtlasWidth'),t.get('m_AtlasHeight'),'pad',t.get('m_AtlasPadding'),'render',t.get('m_AtlasRenderMode'),
                  'pt',fi.get('m_PointSize'),'glyphs',len(t.get('m_GlyphTable',[])),'chars',len(t.get('m_CharacterTable',[])),
                  'free',len(t.get('m_FreeGlyphRects',[])),'used',len(t.get('m_UsedGlyphRects',[])),
                  'src',t.get('m_SourceFontFile'),'fallback',t.get('m_FallbackFontAssetTable'),'tex',[x for x in t.get('m_AtlasTextures',[])], 'fi', {k:v for k,v in fi.items() if k!='m_FamilyName'})
