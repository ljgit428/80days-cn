import UnityPy, os, glob
d=r'F:\Games\80 Days\80 Days_Data'
for f in sorted(glob.glob(d+r'\*.assets'))+[d+r'\Resources\unity default resources']:
    try: env=UnityPy.load(f)
    except Exception as e: print('ERR',f,e); continue
    for o in env.objects:
        if o.type.name=='Font':
            x=o.read()
            fd=getattr(x,'m_FontData',[]) or []
            print(os.path.basename(f), o.path_id, x.m_Name, 'data',len(fd), 'size',getattr(x,'m_FontSize',None),'mode',getattr(x,'m_FontRenderingMode',None),'rects',len(getattr(x,'m_CharacterRects',[]) or []),'names',getattr(x,'m_FontNames',None),'fallback',[ (r.m_PathID) for r in (getattr(x,'m_FallbackFonts',[]) or [])],'charset',getattr(x,'m_CharacterSet',None) if hasattr(x,'m_CharacterSet') else '', 'ascii', getattr(x,'m_ConvertCase',None))
