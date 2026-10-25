import pandas as pd
import streamlit as st

from algo.levels import order_levels
from algo.min_path import min_path, restore_path

# Матрица из задания (стр. 11) + дуги варианта 1: (12,8) цена 4 и (9,10) цена 4.
# Нумерация вершин с 1, как в методичке.
VARIANT_1_ARCS = {
    (1, 9): 2, (2, 17): 2, (3, 5): 4, (3, 7): 5, (3, 11): 3, (4, 9): 2,
    (5, 4): 3, (5, 6): 4, (6, 12): 3, (7, 1): 2, (7, 4): 2, (8, 14): 2,
    (9, 16): 3, (10, 15): 1, (11, 1): 3, (11, 2): 4, (12, 16): 2,
    (13, 15): 2, (14, 15): 2, (16, 10): 3, (16, 13): 3, (17, 8): 2,
    (12, 8): 4, (9, 10): 4,
}
VARIANT_1_SIZE = 17
MAX_VERTICES = 30


def make_df(matrix):
    names = [str(i + 1) for i in range(len(matrix))]
    return pd.DataFrame(matrix, index=names, columns=names)


def variant_1_df():
    matrix = [[0] * VARIANT_1_SIZE for _ in range(VARIANT_1_SIZE)]
    for (i, j), price in VARIANT_1_ARCS.items():
        matrix[i - 1][j - 1] = price
    return make_df(matrix)


def resize_df(df, n):
    old = df.fillna(0).values.tolist()
    matrix = [[0] * n for _ in range(n)]
    for i in range(min(n, len(old))):
        for j in range(min(n, len(old))):
            matrix[i][j] = old[i][j]
    return make_df(matrix)


def reset_to_variant():
    st.session_state.base = variant_1_df()
    st.session_state.n = VARIANT_1_SIZE
    st.session_state.ver += 1


def check_matrix(df):
    """Возвращает список ошибок во введённой матрице (пустой, если всё хорошо)."""
    errors = []
    n = len(df)
    for i in range(n):
        for j in range(n):
            value = df.iat[i, j]
            if pd.isna(value):
                errors.append(f"Ячейка ({i + 1}, {j + 1}) пустая — введите 0, если дуги нет.")
            elif value < 0:
                errors.append(f"Ячейка ({i + 1}, {j + 1}): цена дуги не может быть отрицательной.")
            elif i == j and value != 0:
                errors.append(f"Ячейка ({i + 1}, {i + 1}): петли не допускаются, на диагонали должен быть 0.")
    return errors


def draw_graph(graph, labels, levels=None, path=None):
    """Строит описание графа на языке DOT для st.graphviz_chart."""
    n = len(graph)
    path = path or []
    path_arcs = set(zip(path, path[1:]))

    lines = ["digraph {", "node [shape=circle, fontsize=11];"]
    if levels is None:
        lines.append("layout=circo;")
    else:
        lines.append("rankdir=LR; nodesep=0.3; ranksep=0.9;")
        # подписи уровней сверху + выравнивание вершин одного уровня
        lines.append("node [shape=plaintext];")
        lines.append(" -> ".join(f"N{k}" for k in range(len(levels))) + " [style=invis];")
        lines.append("node [shape=circle];")
        for k, level in enumerate(levels):
            lines.append("{rank=same; N%d; %s}" % (k, "; ".join(str(v) for v in level)))

    for v in range(n):
        style = ', style=filled, fillcolor="#ffd6d6", color=red' if v in path else ""
        lines.append(f'{v} [label="{labels[v]}"{style}];')

    for i in range(n):
        for j in range(n):
            if graph[i][j] != 0:
                style = ", color=red, fontcolor=red, penwidth=2.5" if (i, j) in path_arcs else ""
                lines.append(f'{i} -> {j} [label="{graph[i][j]:g}"{style}];')

    lines.append("}")
    return "\n".join(lines)


st.set_page_config(page_title="ЛР1 — структурный анализ", layout="wide")
st.title("Лабораторная работа №1")
st.caption("Упорядочение вершин графа по уровням и поиск минимального пути")

if "base" not in st.session_state:
    st.session_state.base = variant_1_df()
    st.session_state.n = VARIANT_1_SIZE
    st.session_state.ver = 0

# ---------- 1. Ввод исходных данных ----------
st.header("1. Матрица смежности (цены дуг)")
st.write(
    "В ячейке (i, j) — цена дуги i→j, **0 — дуги нет**. "
    "По умолчанию загружен вариант 1: матрица из задания + дуги (12,8) с ценой 4 и (9,10) с ценой 4."
)

col1, col2 = st.columns([1, 3])
n = col1.number_input("Количество вершин", min_value=2, max_value=MAX_VERTICES, step=1, key="n")
col2.write("")
col2.button("Вернуть данные варианта 1", on_click=reset_to_variant)

if n != len(st.session_state.base):
    st.session_state.base = resize_df(st.session_state.get("edited", st.session_state.base), n)
    st.session_state.ver += 1

edited = st.data_editor(
    st.session_state.base,
    key=f"matrix_{st.session_state.ver}",
    height=(n + 1) * 35 + 3,  # вся матрица без прокрутки
    column_config={c: st.column_config.NumberColumn(c, min_value=0, max_value=1000, step=1, width=55)
                   for c in st.session_state.base.columns},
)
st.session_state.edited = edited

errors = check_matrix(edited)
if errors:
    st.error("Исходные данные некорректны, расчёт невозможен:\n\n" + "\n".join(f"- {e}" for e in errors))
    st.stop()

graph = edited.values.tolist()
arcs_count = sum(1 for row in graph for x in row if x != 0)
if arcs_count == 0:
    st.warning("В графе нет ни одной дуги — введите хотя бы одну ненулевую цену.")
    st.stop()

st.subheader("Исходный граф")
st.graphviz_chart(draw_graph(graph, [str(v + 1) for v in range(n)]))

# ---------- 2. Упорядочение по уровням ----------
st.header("2. Упорядочение вершин по уровням")
levels = order_levels(graph)
placed = [v for level in levels for v in level]

if len(placed) < n:
    rest = sorted(set(range(n)) - set(placed))
    st.error(
        "В графе есть контур, поэтому упорядочить вершины по уровням нельзя. "
        f"Не удалось распределить вершины: {', '.join(str(v + 1) for v in rest)}. "
        "Исправьте матрицу смежности."
    )
    st.stop()

# новая нумерация: подряд по уровням
new_number = {v: k + 1 for k, v in enumerate(placed)}
labels = [f"{new_number[v]}({v + 1})" for v in range(n)]

st.write("Формат вершины: **новый номер (исходный номер)**.")
st.table(pd.DataFrame({
    "Уровень": [f"N{k}" for k in range(len(levels))],
    "Вершины": [", ".join(labels[v] for v in level) for level in levels],
}))

st.subheader("Упорядоченная матрица смежности")
ordered = [[graph[i][j] for j in placed] for i in placed]
ordered_df = make_df(ordered)
st.dataframe(
    ordered_df,
    height=(n + 1) * 35 + 3,
    column_config={c: st.column_config.NumberColumn(c, width=55) for c in ordered_df.columns},
)

# ---------- 3. Минимальный путь ----------
st.header("3. Минимальный путь")
vertex_names = [str(v + 1) for v in range(n)]
col1, col2 = st.columns(2)
start = col1.selectbox("Начальная вершина (исходный номер)", range(n),
                       index=levels[0][0], format_func=lambda v: vertex_names[v])
end = col2.selectbox("Конечная вершина (исходный номер)", range(n),
                     index=levels[-1][-1], format_func=lambda v: vertex_names[v])

path = []
if start == end:
    st.warning("Начальная и конечная вершины совпадают — выберите разные вершины.")
else:
    distances, prev = min_path(graph, levels, start)
    if distances[end] == float("inf"):
        st.warning(f"Из вершины {start + 1} нельзя попасть в вершину {end + 1} — пути не существует.")
    else:
        path = restore_path(prev, end)
        st.success(
            f"Минимальный путь: {' → '.join(labels[v] for v in path)}, "
            f"длина пути = {distances[end]:g}"
        )

st.subheader("Граф, упорядоченный по уровням")
st.graphviz_chart(draw_graph(graph, labels, levels, path))
