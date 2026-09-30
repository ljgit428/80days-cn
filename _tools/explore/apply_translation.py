import UnityPy, json, io, os, sys, shutil, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATA = r'F:\Games\80 Days\80 Days_Data'
ORIG = r'D:\git\project\80 days CN\ORIGINAL_BACKUP\80 Days_Data'
PROJ = r'D:\git\project\80 days CN'
APPLY = os.path.join(PROJ, 'translation', 'zh_apply.json')
ASSETS = os.path.join(PROJ, 'translation', 'zh_assets.json')
PATCHED = os.path.join(PROJ, 'patched')

mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
apply = json.load(io.open(APPLY, encoding='utf-8'))
asset_maps = {}
if os.path.exists(ASSETS):
    asset_maps = json.load(io.open(ASSETS, encoding='utf-8'))

SKIP_KEYS = {'initial','linkPath','divert','func','get','var','name','buildingBlock','condition','params','action','userInfo','set','doFuncs'}
ACTION_TEXT_FIELDS = {
    'Incident': ('text',),
    'SetClue': ('text', 'speaker'),
    'ChangeTransportTitle': ('title',),
}

def is_identifier(s):
    s = s.strip()
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', s):
        return False
    if '_' in s: return True
    if re.search(r'[a-z][A-Z]', s): return True
    if re.search(r'[A-Z]{2,}[a-z]', s): return True
    return False

def has_letters(s):
    t = re.sub(r'<[^>]+>', '', s)
    return bool(re.search(r'[A-Za-z]', t)) and t.strip()

def selected(s, path):
    return bool(path) and has_letters(s) and not is_identifier(s)

def collect_sel(el, path, out):
    if isinstance(el, str):
        if selected(el, path):
            out.append(el)
    elif isinstance(el, list):
        for x in el:
            collect_sel(x, path, out)
    elif isinstance(el, dict):
        if 'action' in el and el['action'] in ACTION_TEXT_FIELDS:
            ui = el.get('userInfo') or {}
            if isinstance(ui, dict):
                for f in ACTION_TEXT_FIELDS[el['action']]:
                    if f in ui and isinstance(ui[f], str) and selected(ui[f], path + '/ui'):
                        out.append(ui[f])
        for k, v in el.items():
            if k in SKIP_KEYS:
                continue
            collect_sel(v, path + '/' + k, out)

def walk_single(o, path, mp, stats):
    if isinstance(o, str):
        if selected(o, path) and o in mp:
            stats[0] += 1
            return mp[o]
        return o
    if isinstance(o, list):
        return [walk_single(x, path, mp, stats) for x in o]
    if isinstance(o, dict):
        nd = {}
        for k, v in o.items():
            if k in SKIP_KEYS:
                nd[k] = v
                continue
            if k == 'userInfo' and isinstance(v, dict) and 'action' in o and o['action'] in ACTION_TEXT_FIELDS:
                ui = dict(v)
                for f in ACTION_TEXT_FIELDS[o['action']]:
                    if f in ui and isinstance(ui[f], str) and selected(ui[f], path + '/ui') and ui[f] in mp:
                        stats[0] += 1
                        ui[f] = mp[ui[f]]
                nd[k] = ui
                continue
            nd[k] = walk_single(v, path + '/' + k, mp, stats)
        return nd
    return o

def read_lines(d):
    script = d.m_Script
    if isinstance(script, str):
        try:
            raw = script.encode('latin-1')
        except Exception:
            raw = script.encode('utf-8', 'surrogateescape')
    else:
        raw = bytes(script)
    try:
        text = raw.decode('utf-8')
    except Exception:
        text = raw.decode('utf-8', 'surrogateescape')
    return text.split('\n')

def fix_zh(z):
    try:
        return z.encode('latin-1').decode('utf-8')
    except Exception:
        return z

def walk_pair(o, c, path, mp, stats):
    if isinstance(o, str):
        if selected(o, path):
            if o in mp:
                stats[0] += 1
                return mp[o]
            stats[1] += 1
            return c
        return c
    if isinstance(o, list):
        if not isinstance(c, list) or len(o) != len(c):
            raise ValueError('structure mismatch at ' + path)
        return [walk_pair(oo, cc, path, mp, stats) for oo, cc in zip(o, c)]
    if isinstance(o, dict):
        if not isinstance(c, dict):
            raise ValueError('structure mismatch at ' + path)
        nd = {}
        for k, v in o.items():
            if k not in c:
                raise ValueError('missing key ' + k + ' at ' + path)
            if k in SKIP_KEYS:
                nd[k] = c[k]
                continue
            if k == 'userInfo' and isinstance(v, dict) and isinstance(c[k], dict) and 'action' in o and o['action'] in ACTION_TEXT_FIELDS:
                ui = dict(c[k])
                for f in ACTION_TEXT_FIELDS[o['action']]:
                    if f in v and isinstance(v[f], str) and selected(v[f], path + '/ui'):
                        if v[f] in mp:
                            stats[0] += 1
                            ui[f] = mp[v[f]]
                        else:
                            stats[1] += 1
                nd[k] = ui
                continue
            nd[k] = walk_pair(v, c[k], path + '/' + k, mp, stats)
        return nd
    return c

if mode == 'apply':
    os.makedirs(PATCHED, exist_ok=True)
    bak = os.path.join(PATCHED, 'resources.assets.before_textpatch')
    if not os.path.exists(bak):
        shutil.copy(os.path.join(DATA, 'resources.assets'), bak)
        print('backup saved:', bak)

env_o = UnityPy.load(ORIG)
env = UnityPy.load(DATA)

orig_lines = None
for obj in env_o.objects:
    if obj.type.name == 'TextAsset':
        d = obj.read()
        if d.m_Name == '80days.inkcontent':
            orig_lines = read_lines(d)
            break
if orig_lines is None:
    print('ERROR: original inkcontent not found')
    sys.exit(1)
print('original lines:', len(orig_lines))

orig_assets = {}
for obj in env_o.objects:
    if obj.type.name == 'TextAsset':
        dd = obj.read()
        if dd.m_Name in asset_maps:
            sc = dd.m_Script
            orig_assets[dd.m_Name] = sc if isinstance(sc, str) else bytes(sc).decode('utf-8', 'surrogateescape')

report = []
changed_files = set()
for obj in env.objects:
    if obj.type.name != 'TextAsset':
        continue
    d = obj.read()
    if d.m_Name in asset_maps:
        mp0src = asset_maps[d.m_Name]
        script0 = d.m_Script
        text0 = script0 if isinstance(script0, str) else bytes(script0).decode('utf-8', 'surrogateescape')
        orig_text = orig_assets.get(d.m_Name)
        if orig_text is None:
            print('asset', d.m_Name, ': no original found, skip')
            continue
        try:
            onode0 = json.loads(orig_text)
            cnode0 = json.loads(text0)
        except Exception as e:
            print('asset', d.m_Name, 'parse error:', e)
            continue
        sel = []
        collect_sel(onode0, '', sel)
        seen = set(); uniq = []
        for x in sel:
            if x not in seen:
                seen.add(x); uniq.append(x)
        missing = [x for x in uniq if x not in mp0src]
        if missing:
            print('asset', d.m_Name, 'missing keys:', len(missing), missing[:3])
        mp0 = {x: mp0src[x] for x in uniq if x in mp0src}
        stats0 = [0, 0]
        try:
            newnode0 = walk_pair(onode0, cnode0, '', mp0, stats0)
        except Exception as e:
            print('asset', d.m_Name, 'walk error:', e)
            continue
        print('asset map check:', d.m_Name, 'replacements:', stats0[0])
        if stats0[0] and mode == 'apply':
            d.m_Script = json.dumps(newnode0, ensure_ascii=False, indent=2)
            d.save()
            changed_files.add(obj.assets_file.name)
            print('patched asset map:', d.m_Name)
        continue
    if d.m_Name != '80days.inkcontent':
        continue
    lines = read_lines(d)
    changed = False
    for ln, pair in apply.items():
        i = int(ln)
        if i >= len(lines) or i >= len(orig_lines):
            continue
        try:
            onode = json.loads(orig_lines[i])
            cnode = json.loads(lines[i])
        except Exception:
            continue
        sel = []
        collect_sel(onode, '', sel)
        seen = set(); uniq = []
        for s0 in sel:
            if s0 not in seen:
                seen.add(s0); uniq.append(s0)
        if len(uniq) != len(pair['zh']):
            print('line', i, 'count mismatch', len(uniq), len(pair['zh']))
            continue
        mp = dict(zip(uniq, [fix_zh(z) for z in pair['zh']]))
        stats = [0, 0]
        try:
            newnode = walk_pair(onode, cnode, '', mp, stats)
        except Exception as e:
            print('line', i, 'parallel walk error, fallback to original structure:', e)
            stats = [0, 0]
            newnode = walk_single(onode, '', mp, stats)
        if stats[0] == 0:
            continue
        lines[i] = json.dumps(newnode, ensure_ascii=False, separators=(',', ':'))
        changed = True
        report.append((i, stats[0], stats[1]))
    if changed and mode == 'apply':
        d.m_Script = '\n'.join(lines)
        d.save()
        changed_files.add(obj.assets_file.name)
        print('patched TextAsset:', d.m_Name)

print('replaced lines (%d):' % len(report), report)
if mode == 'apply' and (report or changed_files):
    env.save(out_path=PATCHED)
    for fn in changed_files:
        shutil.copy(os.path.join(PATCHED, fn), os.path.join(DATA, fn))
        print('copied', fn, 'to game, size:', os.path.getsize(os.path.join(DATA, fn)))
