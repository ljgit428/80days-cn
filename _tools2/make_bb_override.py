# 生成中文数字版 print_num / Cprint_num，写入 translation/bb_override.json（apply.py 会用它覆盖原 buildingBlock）
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = '0123456789'
def g(v): return {"get": v}
def f(name, *p): return {"func": name, "params": list(p)}
def IF(c, then, other=None):
    d = {"condition": c, "then": then}
    if other is not None: d["otherwise"] = other
    return d
def digit(e):
    node = [D[9]]
    for i in range(8, -1, -1):
        node = [IF(f("Equals", e, i), [D[i]], node)]
    return node
def make(var, name):
    """阿拉伯数字：n>=10 时先递归输出 n/10，再输出个位"""
    n = g(var)
    rec = {"buildingBlock": name, "params": {var: f("Divide", n, 10)}}
    return [IF(f("GreaterThanOrEqualTo", n, 10), [rec])] + digit(f("Mod", n, 10))
out = {"print_num": make("__bbprint_num0", "print_num"), "Cprint_num": make("__bbCprint_num0", "Cprint_num")}
json.dump(out, open(os.path.join(ROOT, 'translation', 'bb_override.json'), 'w', encoding='utf-8'), ensure_ascii=False)
if __name__ == '__main__':
    # 简易解释器自测
    def ev(e, env):
        if isinstance(e, int): return e
        if 'get' in e: return env[e['get']]
        a = [ev(x, env) for x in e['params']]
        return {'Equals': lambda: a[0]==a[1], 'GreaterThan': lambda: a[0]>a[1], 'LessThan': lambda: a[0]<a[1],
                'GreaterThanOrEqualTo': lambda: a[0]>=a[1], 'And': lambda: a[0] and a[1],
                'Divide': lambda: int(a[0]/a[1]), 'Multiply': lambda: a[0]*a[1], 'Mod': lambda: a[0]%a[1]}[e['func']]()
    def run(content, env):
        s = ''
        for x in content:
            if isinstance(x, str): s += x
            elif 'condition' in x: s += run(x['then'] if ev(x['condition'], env) else x.get('otherwise', []), env)
            elif 'buildingBlock' in x:
                k, v = next(iter(x['params'].items())); s += run(out[x['buildingBlock']], {k: ev(v, env)})
        return s
    for t in [0, 3, 10, 15, 20, 21, 99, 100, 105, 110, 115, 250, 999, 1000, 1005, 1015, 1200, 2500, 10000, 12345, 960000]:
        print(t, run(out['print_num'], {'__bbprint_num0': t}))
