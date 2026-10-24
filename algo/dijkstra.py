import heapq

def min_path(graph: list[list[float]], start_vertex_index: int) -> list[float]:
    """
    Алгоритм Дейкстры для графа, заданного матрицей смежности.
    
    :param graph: list[list[float]] — матрица смежности размером n×n,
                   где graph[i][j] — вес ребра i→j.
                   Отсутствие ребра обозначается 0 или float('inf').
    :param start_vertex_index: int — индекс начальной вершины (0-based).
    :return: (dist list[float]) — 
            dist[i] — кратчайшее расстояние от start_vertex_index до i,
    """
    
    n = len(graph)
    INF = float('inf')
    visited = [False] * n
    distances = [INF] * n
    
    distances[start_vertex_index] = 0
    pq = [(0, start_vertex_index)]
    
    while pq:
        dist, vert = heapq.heappop(pq)

        if visited[vert]:
            continue
        visited[vert] = True

        for v in range(n):
            weight = graph[vert][v]
            if weight == 0 or weight == INF:
                continue

            nd = dist + weight
            if nd < distances[v]:
                distances[v] = nd
                heapq.heappush(pq, (nd, v))

    return distances
