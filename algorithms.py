from collections import deque

def bfs(n,edges,start,end):
    steps=[]
    if start == end:
        steps.append(['finish',start])
        return steps

    queue=deque([start])
    used=[-1]*n
    used[start]=start
    can=False

    while queue:
        node=queue.popleft()
        steps.append(['edge', used[node],node])
        for edge in edges[node]:
            if used[edge]==-1:
                used[edge]=node
                if edge==end:
                    can=True
                    curr=edge
                    steps.append(['edge',node,edge])
                    break
                queue.append(edge)
                steps.append(['queue',edge])
        if can:
            break
    if can:
        steps.append(['finish',curr])
        if curr!=start:
            curr=used[curr]
        while curr!=start:
            steps.append(['return', curr, steps[-1][1]])
            curr=used[curr]
        steps.append(['return', start,steps[-1][1]])
        return steps
    else:
        return steps

def dfs(n,edges,start,end):
    steps=[]
    if start == end:
        steps.append(['finish', start])
        return steps

    stack=[start]
    used=[-1]*n
    used[start]=start
    can=False

    while stack:
        node=stack.pop()
        steps.append(['edge', used[node],node])
        for edge in edges[node]:
            if used[edge]==-1:
                used[edge]=node
                if edge==end:
                    can=True
                    curr=edge
                    steps.append(['edge',node,edge])
                    break
                stack.append(edge)
                steps.append(['queue',edge])
        if can:
            break
    if can:
        steps.append(['finish', curr])
        if curr != start:
            curr = used[curr]
        while curr != start:
            steps.append(['return', curr, steps[-1][1]])
            curr = used[curr]
        steps.append(['return', start, steps[-1][1]])
        return steps
    else:
        return steps

