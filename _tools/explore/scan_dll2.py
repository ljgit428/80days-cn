import re
p=r'F:\Games\80 Days\80 Days_Data\Managed\Assembly-CSharp.dll'
b=open(p,'rb').read()
for w in [b'RequestCharactersInTexture',b'textureRebuilt',b'GetCharacterInfo',b'TextMesh',b'TextGenerator',b'CharacterInfo',b'fontSize',b'Font',b'set_text',b'TextMeshPro',b'NGUI',b'UILabel',b'BMFont',b'wordWrap',b'horizontalOverflow',b'Split',b'LineBreak',b'WordWrap',b'SplitIntoWords']:
    print(w.decode(), b.count(w))
names=set(re.findall(rb'[A-Za-z_][A-Za-z0-9_]{3,40}',b))
print(sorted(n.decode() for n in names if re.search(rb'(?i)text|font|glyph|word|line|wrap|typewrit|letter',n))[:400])
