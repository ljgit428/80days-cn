# 把本地明文译文（含英文原文，不公开）导出为哈希键版本 translation/hashed/*.json（可公开）
# 用法: python export_public.py
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
from hashkey import H
T = os.path.join(ROOT, 'translation'); O = os.path.join(T, 'hashed'); os.makedirs(O, exist_ok=True)
L = lambda f: json.load(open(os.path.join(T, f), encoding='utf-8'))
def W(f, d): json.dump(d, open(os.path.join(O, f), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0, sort_keys=True)
KEEP = '@='   # 译文与原文相同（保留英文，如调试文本、地名标签）时不写出原文，只写标记
V = lambda k, v: KEEP if v == k else v
def flat(d): return {H(k): V(k, v) for k, v in d.items()}
W('tm_zh.json', flat(L('tm_zh.json')))
W('tm_line.json', {sc: flat(d) for sc, d in L('tm_line.json').items()})
W('code_strings.json', {sc: {'#' + H(k): V(k, v) for k, v in d.items()} for sc, d in L('code_strings.json').items()})
W('ui_scene.json', flat(L('ui_scene.json')))
# ink 补丁：seq 里的英文片段换成 #哈希；expect（子串检查）换成整个元素的哈希 expect_h
src = open(os.path.join(ROOT, 'extracted', '80days.inkcontent'), encoding='utf-8').read().split('\n')
out = []
for x in L('ink_patches.json'):
    x = dict(x)
    if 'seq' in x: x['seq'] = [q if q.startswith('@') else '#' + H(q) for q in x['seq']]
    if 'expect' in x:
        d = json.loads(src[x['line']]); c = d['stitches'][x['stitch']]['content'] if x.get('stitch') else d
        el = json.dumps(c[x['index']], ensure_ascii=False, separators=(',', ':'))
        assert x['expect'] in json.dumps(c[x['index']], ensure_ascii=False)
        x['expect_h'] = H(el); del x['expect']
    out.append(x)
json.dump(out, open(os.path.join(O, 'ink_patches.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
import shutil; shutil.copy(os.path.join(T, 'bb_override.json'), os.path.join(O, 'bb_override.json'))
print('exported ->', O, sorted(os.listdir(O)))
