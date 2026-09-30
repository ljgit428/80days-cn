import json,sys,re
ink=open('work/ink.txt',encoding='utf-8').read().split('\n')
lst=[json.loads(l.split(' ',1)[1]) for l in open('work/list.txt',encoding='utf-8') if l.strip()]
cur=None;hits={}
lines=[]
for ln in ink:
    if ln.startswith('===='): cur=ln[5:]; continue
    lines.append((cur,ln))
used=set()
for i,s in enumerate(lst):
    k=s.strip()[:50]
    for j,(c,ln) in enumerate(lines):
        if k and k in ln:
            used.add(j);break
out=[];last=None
for j in sorted(used):
    c,ln=lines[j]
    if c!=last: out.append('==== '+c); last=c
    out.append(ln)
print('\n'.join(out))
