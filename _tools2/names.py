import json,sys
tm=json.load(open('translation/tm_zh.json'))
for w in sys.argv[1:]:
    hits=[(k,v) for k,v in tm.items() if w in k and len(k)<130][:1]
    for k,v in hits: print(w,'|',k[:80],'=>',v[:80])
