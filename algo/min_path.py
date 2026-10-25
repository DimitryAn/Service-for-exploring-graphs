def min_path(graph: list[list[float]], levels: list[list[int]], start_vertex_index: int) -> tuple[list[float], list[int]]:
    """
    Минимальный путь на графе без контуров по формуле (1.7) из методички
    (динамическое программирование по уровням):
        q(a1, aj) = min [ q(a1, ai) + q(ai, aj) ],  ai из G^-1(aj)

    :param graph: list[list[float]] — матрица смежности размером n×n,
                   где graph[i][j] — цена дуги i→j, 0 — дуги нет.
    :param levels: list[list[int]] — уровни из order_levels.
    :param start_vertex_index: int — индекс начальной вершины (0-based).
    :return: (dist list[float], prev list[int]) —
            dist[i] — длина минимального пути от start_vertex_index до i (inf, если пути нет),
            prev[i] — предыдущая вершина на этом пути (-1, если её нет).
    """

    n = len(graph)
    INF = float('inf')
    distances = [INF] * n
    prev = [-1] * n
    distances[start_vertex_index] = 0

    # идём строго по уровням: все предшественники вершины j уже посчитаны
    for level in levels:
        for j in level:
            for i in range(n):
                # i — вершина из G^-1(j), т.е. есть дуга i→j
                if graph[i][j] != 0 and distances[i] + graph[i][j] < distances[j]:
                    distances[j] = distances[i] + graph[i][j]
                    prev[j] = i

    return distances, prev


def restore_path(prev: list[int], end_vertex_index: int) -> list[int]:
    """
    Восстановление пути по массиву предков из min_path.

    :return: list[int] — вершины пути от начальной до end_vertex_index (0-based).
    """

    path = []
    v = end_vertex_index
    while v != -1:
        path.append(v)
        v = prev[v]
    return path[::-1]
