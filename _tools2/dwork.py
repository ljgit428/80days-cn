# 数据文件待译清单: python3 dwork.py FILE [start] [count]  -> /tmp/todo.json, /tmp/todo_line.json, work/dlist.txt
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
f=sys.argv[1]; st=int(sys.argv[2]) if len(sys.argv)>2 else 0; cnt=int(sys.argv[3]) if len(sys.argv)>3 else 150
tm=json.load(open(os.path.join(ROOT,'translation','tm_zh.json'),encoding='utf-8'))
tml=json.load(open(os.path.join(ROOT,'translation','tm_line.json'),encoding='utf-8'))
sc=tml.get(f,{})
d=json.load(open(os.path.join(EXT,f),encoding='utf-8-sig'))
seen={}; 
def cb(s,p):
    if s in tm or s in sc or s in seen: return
    seen[s]=p
walk_data(d,DATA_RULES[f],cb)
items=list(seen.items())
print('remaining',len(items),'chars',sum(len(k) for k,_ in items))
items=items[st:st+cnt]
json.dump([k for k,_ in items],open('/tmp/todo.json','w'),ensure_ascii=False)
json.dump([f]*len(items),open('/tmp/todo_line.json','w'))
with open(os.path.join(ROOT,'work','dlist.txt'),'w') as o:
    for i,(k,p) in enumerate(items): o.write(f'{i} [{p[-40:]}] {json.dumps(k,ensure_ascii=False)}\n')
