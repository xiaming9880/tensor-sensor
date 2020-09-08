import sys
import graphviz

from tsensor.explain import _shape
from tsensor.parse import *
from tsensor.ast import *



def matrix_html(nrows, ncols, label, fontsize=12, fontname="Consolas", dimfontsize=9, color="#cfe2d4"):
    isvec = ncols==None
    if isvec:
        sz = str(nrows)
        ncols=nrows
        nrows=1
    else:
        sz = f"{nrows}x{ncols}"
    w = ncols*20
    h = nrows*20
    if ncols==1:
        w = 15
    if nrows==1:
        h = 15
    html = f"""
    <table fixedsize="true" width="{w}" height="{h+2*fontsize*1.1}" BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">
    <tr>
    <td fixedsize="true" width="{w}" height="{fontsize*1.1}" cellspacing="0" cellpadding="0" border="0" valign="bottom" align="center">
    <font face="{fontname}" color="#444443" point-size="{dimfontsize}">{sz}</font>
    </td>
    </tr>
    <tr>    
    <td fixedsize="true" width="{w}" height="{h}" cellspacing="0" cellpadding="0" bgcolor="{color}" border="1" sides="ltbr" align="center">
    <font face="{fontname}" color="#444443" point-size="{fontsize}">{label}</font>
    </td>
    </tr>
    </table>"""
    return html


W = torch.tensor([[1, 2], [3, 4], [5, 6]])
b = torch.tensor([9, 10]).reshape(2, 1)
x = torch.tensor([4, 5]).reshape(2, 1)
h = torch.tensor([1, 2])
a = 3

p = PyExprParser("b = W@b + h.dot(h)")
print(p.tokens)
root = p.parse()
nodes = postorder(root)
atoms = leaves(root)
# map tokens to nodes
tok2node = {}
for nd in atoms:
    tok2node[nd.token] = nd
frame = sys._getframe()
result = root.eval(frame)

nodesS = set(nodes)
atomsS = set(atoms)
ops = nodesS.difference(atomsS)

s = """
digraph G {
    nodesep=.0;
    ranksep=.3;
    rankdir=BT;
    ordering=out; # keep order of leaves
"""

fontname="Consolas"
fontsize=12
spread = .2

s += f'{{ rank=same; '
for t in p.tokens:
    if t.type!=ENDMARKER:
        x = tok2node[t] if t in tok2node else t
        shape = ""
        sh = _shape(x.value)
        label = f'<font face="{fontname}" color="#444443" point-size="{fontsize}">{t.value}</font>'
        matrixcolor="#cfe2d4"
        vectorcolor="#fefecd"
        if x in atomsS and sh is not None:
            if len(sh)==1:
                label = matrix_html(sh[0],None,t.value,fontname=fontname,fontsize=fontsize,color=vectorcolor)
            elif len(sh)==2:
                label = matrix_html(sh[0],sh[1],t.value,fontname=fontname,fontsize=fontsize,color=matrixcolor)
        # margin/width don't seem to do anything for shape=plain
        if t.type==DOT:
            spread=.1
        if t.type==EQUAL:
            spread=.25
        if t.type in ADDOP:
            spread=.5
        if t.type in MULOP:
            spread=.2
        s += f'leaf{id(x)} [shape=box penwidth=0 margin=.001 width={spread} label=<{label}>]\n'
s += '}\n'

s += "}\n"

graphviz.Source(s).view()