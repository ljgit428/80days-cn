# 回填译文 -> 重建 TextAsset -> 写回 resources.assets（原版取自 ORIGINAL_BACKUP）-> 复制到游戏目录
# 用法: python apply.py [--no-install]
import json, os, sys, re, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from hashkey import H
# 优先用本地明文译文（translation/*.json，含英文原文，不入库）；没有则用公开的哈希键版本 translation/hashed/
_T = os.path.join(ROOT, 'translation')
HASHED = not os.path.exists(os.path.join(_T, 'tm_zh.json'))
TDIR = os.path.join(_T, 'hashed') if HASHED else _T
K = H if HASHED else (lambda s: s)
TM = json.load(open(os.path.join(TDIR, 'tm_zh.json'), encoding='utf-8'))
_pl = os.path.join(TDIR, 'tm_line.json')
TML = json.load(open(_pl, encoding='utf-8')) if os.path.exists(_pl) else {}
print('译文来源:', TDIR)
stat = {'hit': 0, 'miss': 0}
CUR = {'line': None}
def cb(s, p):
    sc = CUR['line']; k = K(s); z = TML.get(sc, {}).get(k)
    if z is None and sc and sc.startswith('bb:'): z = TML.get('bb', {}).get(k)
    if z is None: z = TM.get(k)
    if z == '@=': z = s   # 公开版里“与原文相同”的标记
    if z is None:
        stat['miss'] += 1
        if os.environ.get('SHOWMISS'): print('MISS', sc, repr(s)[:120])
        return None
    stat['hit'] += 1; return z

PUNCT = {'.': '。', ',': '，', '!': '！', '?': '？', ';': '；', ':': '：', '...': '……', '…': '……'}
def cn_punct(s):   # 纯标点碎片 -> 中文标点
    t = s.strip()
    if not t: return '' if '\n' not in s else s
    if t in ('"', "'"): return t   # 单独的引号无法判断开/合，保留原样
    if re.fullmatch(r'[.,!?;:…]+', t):
        return PUNCT.get(t) or ''.join(PUNCT.get(c, c) for c in t)
    if re.fullmatch(r'[.,!?;:…]*["\']?[.,!?;:…]*', t):   # 如 ." 或 ," -> 。” ，”
        return ''.join(PUNCT.get(c, '”' if c == '"' else '’' if c == "'" else c) for c in t)
    return s
def blank_spaces(el):   # 整行都已汉化时，去掉纯空格片段、纯标点转中文（中文不需要词间空格）
    if isinstance(el, str): return cn_punct(el) if not re.search(r'[A-Za-z0-9<>]', el) else el
    if isinstance(el, list): return [blank_spaces(x) for x in el]
    if isinstance(el, dict): return {k: (blank_spaces(v) if k in ('content','then','otherwise','cycle','sequence','shuffle','onceonly','stitches') or k.startswith('__') or isinstance(v,(list,dict)) and k not in SKIP_KEYS else v) for k, v in el.items()}
    return el

out = {}
# 1) inkcontent
lines = open(os.path.join(EXT, '80days.inkcontent'), encoding='utf-8').read().split('\n')
new_lines = []
pp = os.path.join(TDIR, 'ink_patches.json')
PATCH = {}
for x in (json.load(open(pp, encoding='utf-8')) if os.path.exists(pp) else []):
    PATCH.setdefault(x['line'], []).append(x)
def seq_patch(el, x):   # 在任意列表中找 [A, @bb, C] 这样的相邻序列，把指定位置替换
    if isinstance(el, dict):
        for v in el.values(): seq_patch(v, x)
    elif isinstance(el, list):
        pat = x['seq']
        for j in range(len(el) - len(pat) + 1):
            ok = all((isinstance(el[j+t], dict) and el[j+t].get('buildingBlock') == q[1:]) if q.startswith('@') else (isinstance(el[j+t], str) and H(el[j+t]) == q[1:]) if q.startswith('#') else el[j+t] == q for t, q in enumerate(pat))
            if ok:
                for t, v in x.get('set', {}).items(): el[j + int(t)] = v
                for t, v in sorted(x.get('ins', {}).items(), key=lambda kv: -int(kv[0])): el.insert(j + int(t), v)
                x['_hits'] = x.get('_hits', 0) + 1
                if x.get('ins'): break
        for v in el: seq_patch(v, x)
def patch_line(i, d):   # 节点级补丁
    CUR['line'] = str(i)
    for x in PATCH.get(i, []):
        if 'seq' in x:
            seq_patch(d, x); assert x.get('_hits'), ('seq 补丁未命中', x); continue
        c = d['stitches'][x['stitch']]['content'] if x.get('stitch') else d
        if 'expect_h' in x: assert H(json.dumps(c[x['index']], ensure_ascii=False, separators=(',', ':'))) == x['expect_h'], ('补丁不匹配', x)
        else: assert x['expect'] in json.dumps(c[x['index']], ensure_ascii=False), ('补丁不匹配', x)
        c[x['index']] = x['replace']
    return d
for i, ln in enumerate(lines):
    if not ln.strip(): new_lines.append(ln); continue
    before = stat['miss']
    d = walk_ink(patch_line(i, json.loads(ln)), cb)
    if stat['miss'] == before and ln != json.dumps(d, ensure_ascii=False, separators=(',', ':')):
        d = blank_spaces(d)
    new_lines.append(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
ink = '\n'.join(new_lines)
out['80days.inkcontent'] = ink
# 2) 80days：buildingBlocks 汉化 + 按新字节偏移重建 ranges
d80 = json.load(open(os.path.join(EXT, '80days'), encoding='utf-8'))
old_raw = open(os.path.join(EXT, '80days.inkcontent'), 'rb').read().split(b'\n')
old_start = {}; o = 0
for i, l in enumerate(old_raw): old_start[o] = i; o += len(l) + 1
new_raw = [l.encode('utf-8') for l in new_lines]
new_start = []; o = 0
for l in new_raw: new_start.append(o); o += len(l) + 1
rng = d80['indexed-content']['ranges']
for k, v in rng.items():
    i = old_start[int(v.split()[0])]
    rng[k] = f'{new_start[i]} {len(new_raw[i]) + 1}'
def _bb(k, v):
    CUR['line'] = 'bb:' + k; before = stat['miss']
    v = walk_ink(v, cb, '/bb')
    return blank_spaces(v) if stat['miss'] == before else v   # 模块已全部汉化：去掉词间空格
d80['buildingBlocks'] = {k: _bb(k, v) for k, v in d80['buildingBlocks'].items()}
ov = os.path.join(TDIR, 'bb_override.json')
if os.path.exists(ov):   # 整块替换的中文逻辑（如中文数字 print_num）
    for k, v in json.load(open(ov, encoding='utf-8')).items():
        assert k in d80['buildingBlocks'], k
        d80['buildingBlocks'][k] = v
out['80days'] = json.dumps(d80, ensure_ascii=False, separators=(',', ':'))
# 3) 数据文件
for f, keys in DATA_RULES.items():
    CUR['line'] = f
    d = json.load(open(os.path.join(EXT, f), encoding='utf-8'))
    out[f] = json.dumps(walk_data(d, keys, cb), ensure_ascii=False, indent=4)
print('hit', stat['hit'], 'miss(occurrences)', stat['miss'])

os.makedirs(os.path.join(ROOT, 'patched', 'textassets'), exist_ok=True)
for n, s in out.items():
    open(os.path.join(ROOT, 'patched', 'textassets', n), 'w', encoding='utf-8', newline='').write(s)
if '--no-install' in sys.argv: sys.exit()

import UnityPy
src_dir = os.path.join(ROOT, 'ORIGINAL_BACKUP', '80 Days_Data')
env = UnityPy.load(os.path.join(src_dir, 'resources.assets'))
done = set()
for obj in env.objects:
    if obj.type.name == 'TextAsset':
        t = obj.read()
        if t.m_Name in out:
            t.m_Script = out[t.m_Name]; t.save(); done.add(t.m_Name)
print('replaced', sorted(done))
assert done == set(out), set(out) - done
pdir = os.path.join(ROOT, 'patched'); env.save(out_path=pdir)
dst = r'F:\Games\80 Days\80 Days_Data\resources.assets'
shutil.copy(os.path.join(pdir, 'resources.assets'), dst)
print('installed ->', dst, os.path.getsize(dst))
