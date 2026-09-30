import UnityPy, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = r'F:\Games\80 Days\80 Days_Data'
env = UnityPy.load(base)

# Look for TMP font assets and UI text in MonoBehaviours
from collections import Counter

texts = []
mono_scripts = {}
for obj in env.objects:
    if obj.type.name == 'MonoScript':
        try:
            d = obj.read()
            mono_scripts[obj.path_id] = d.m_ClassName
        except Exception:
            pass

# Find MonoBehaviour class distribution
cls_counter = Counter()
for obj in env.objects:
    if obj.type.name == 'MonoBehaviour':
        try:
            d = obj.read()
            n = d.m_Script
            # m_Script is a PPtr; get class name via mono_scripts if possible
        except Exception:
            pass

# Simpler: dump MonoBehaviour raw and look for text-like fields
# But that's heavy. Instead: search all objects for 'Text'/'Button' UnityEngine UI components
print('=== Looking for UI Text / Button components in objects ===')

# Try reading components attached to GameObjects via prefab structure is complex.
# Instead let's brute-force: serialize each MonoBehaviour's type tree dump and grep for strings.
found = []
for obj in env.objects:
    if obj.type.name != 'MonoBehaviour':
        continue
    try:
        tree = obj.read_typetree()
    except Exception:
        continue
    if not isinstance(tree, dict):
        continue
    # look for common text fields
    for key in ('m_Text', 'text', 'Text', 'label', 'm_Label', 'm_Title', 'title', 'm_Tooltip'):
        if key in tree and isinstance(tree[key], str) and tree[key].strip():
            found.append((obj.assets_file.name, key, tree[key][:120]))
    # nested
    for k, v in tree.items():
        if isinstance(v, dict):
            for key2 in ('m_Text','text','Text'):
                if key2 in v and isinstance(v[key2], str) and v[key2].strip():
                    found.append((obj.assets_file.name, f'{k}.{key2}', v[key2][:120]))

print('found text-ish fields:', len(found))
seen = set()
for f in found:
    key = (f[0], f[2])
    if key in seen:
        continue
    seen.add(key)
    print(f'  [{f[0]}] {f[1]}: {f[2]!r}')
