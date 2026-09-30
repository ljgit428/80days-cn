import UnityPy, os, glob, collections
d=r'F:\Games\80 Days\80 Days_Data'
env=UnityPy.load(d+r'\sharedassets1.assets')
c=collections.Counter(); errs=collections.Counter()
for o in env.objects:
    if o.type.name=='MonoBehaviour':
        try:
            x=o.read(); s=x.m_Script.read(); c[s.m_ClassName]+=1
        except Exception as e: errs[str(e)[:80]]+=1
print(c.most_common(60)); print(errs.most_common(5))
print(env.objects[0].assets_file.unity_version if hasattr(env.objects[0],'assets_file') else '')
