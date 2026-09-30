import UnityPy, os, glob, collections
d=r'F:\Games\80 Days\80 Days_Data'
print(os.listdir(d+r'\Managed'))
for f in sorted(glob.glob(d+r'\*.assets')):
    env=UnityPy.load(f); c=collections.Counter()
    for o in env.objects:
        if o.type.name=='MonoBehaviour':
            try:
                x=o.read(); s=x.m_Script.read(); c[s.m_ClassName]+=1
                if s.m_ClassName in ('TMP_FontAsset',): print(os.path.basename(f),o.path_id,x.m_Name)
            except Exception as e: c['ERR']+=1
        if o.type.name=='MonoScript':
            pass
    print(os.path.basename(f), [(k,v) for k,v in c.items() if any(t in k for t in ('TMP','Text','Word','Story','Font'))])
