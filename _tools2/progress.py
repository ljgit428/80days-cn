# 汉化总进度：按英文字符数统计已翻译比例
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
tm = json.load(open(os.path.join(ROOT,'translation','tm_zh.json'),encoding='utf-8'))
tml = json.load(open(os.path.join(ROOT,'translation','tm_line.json'),encoding='utf-8'))
lines = open(os.path.join(EXT,'80days.inkcontent'),encoding='utf-8').read().split('\n')
tot=done=0; ln_done=ln_tot=0
for i,l in enumerate(lines):
    if not l.strip(): continue
    a=[0,0]
    def f(s,p):
        a[0]+=len(s)
        if s in tm or s in tml.get(str(i),{}): a[1]+=len(s)
    walk_ink(json.loads(l),f)
    if a[0]:
        ln_tot+=1; ln_done+= a[0]==a[1]
    tot+=a[0]; done+=a[1]
print(f'剧情文本(ink)：{done/tot*100:.1f}%  （{done:,}/{tot:,} 字符，完成 {ln_done}/{ln_tot} 段）')
