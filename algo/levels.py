def order_levels(graph: list[list[float]]) -> list[list[int]]:
    """
    Упорядочение вершин графа по уровням (порядковая функция на графе).

    :param graph: list[list[float]] — матрица смежности размером n×n,
                   где graph[i][j] — вес дуги i→j, 0 — дуги нет.
    :return: list[list[int]] — уровни N0, N1, ... (индексы вершин 0-based).
             Если в графе есть контур, часть вершин никуда не попадёт,
             поэтому вызывающий код должен проверить, что распределены все n вершин.
    """

    n = len(graph)
    placed = set()
    levels = []

    while len(placed) < n:
        level = []
        for j in range(n):
            if j in placed:
                continue
            # в вершину j входят дуги только из вершин предыдущих уровней
            if all(graph[i][j] == 0 or i in placed for i in range(n)):
                level.append(j)

        # ни одну вершину добавить нельзя — значит, остался контур
        if not level:
            break

        levels.append(level)
        placed.update(level)

    return levels
