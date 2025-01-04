#導入套件，開始使用的前置步驟
from graphviz import Digraph
dot = Digraph(comment='The Round Table')
#新增一個點 A，顯示名稱為 QQ
dot.node('A', label = 'QQ') 
#新增一個點 B，顯示名稱為 www
dot.node('B', label = 'www')
#新增一個從點 A 到點 B 的邊，顯示名稱為 Like
dot.edge("A", "B", label = "Like")
from graphviz import Digraph
dot = Digraph(comment='The Round Table')
names = ['剪刀', '石頭', '布']
for i in names:  #新增三個結點，分別叫做剪刀石頭布
    dot.node(i, i)
for i in range(len(names)): #將互相克制的關係畫上去
    dot.edge(names[i], names[i-1], "克制")
dot
#匯出成 pdf 檔案
dot.render('./round-table.gv', view=True)
#顯示 Graphviz 標記碼
str(dot)