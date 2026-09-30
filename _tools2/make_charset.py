# -*- coding: utf-8 -*-
"""生成 cn_charset.txt：译文用到的全部字符，供运行时预热图集使用。
放到游戏根目录 F:\\Games\\80 Days\\cn_charset.txt"""
import os, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'D:\git\project\80 days CN'
GAME = r'F:\Games\80 Days'
chars = set()
def eat(x):
    if isinstance(x, str): chars.update(x)
    elif isinstance(x, dict):
        for v in x.values(): eat(v)
    elif isinstance(x, list):
        for v in x: eat(v)
for n in ['tm_zh.json', 'tm_line.json', 'code_strings.json', 'ui_scene.json', 'bb_override.json', 'ink_patches.json']:
    p = os.path.join(ROOT, 'translation', n)
    if os.path.exists(p):
        d = json.load(open(p, encoding='utf-8'))
        eat(list(d.values()) if n == 'tm_zh.json' else d)
sel = sorted(c for c in chars if ord(c) > 0x2E7F)     # 需要走中文后备的字符
out = ''.join(sel)
open(os.path.join(GAME, 'cn_charset.txt'), 'w', encoding='utf-8').write(out)
print('chars needing CJK fallback:', len(sel))
print('written ->', os.path.join(GAME, 'cn_charset.txt'))
