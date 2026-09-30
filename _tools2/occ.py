# 字符串 -> 出现的作用域集合（ink 行号 / bb:模块 / 数据文件名）
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
def build():
    occ = collections.defaultdict(set)
    lines = open(os.path.join(EXT, '80days.inkcontent'), encoding='utf-8').read().split('\n')
    for i, ln in enumerate(lines):
        if ln.strip(): walk_ink(json.loads(ln), lambda s, p: occ[s].add(str(i)))
    bb = json.load(open(os.path.join(EXT, '80days'), encoding='utf-8'))['buildingBlocks']
    for k, v in bb.items(): walk_ink(v, lambda s, p: occ[s].add('bb:' + k), '/bb')
    for f, keys in DATA_RULES.items():
        walk_data(json.load(open(os.path.join(EXT, f), encoding='utf-8')), keys, lambda s, p: occ[s].add(f))
    return occ, list(bb)
