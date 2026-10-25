# Service for exploring graphs

Лабораторная работа №1 (УБС): упорядочение вершин графа по уровням и поиск минимального пути. Вариант 1.

## Запуск

Через Docker:

```
docker build -t graphs-lab1 .
docker run --rm -p 8501:8501 graphs-lab1
```

Без Docker:

```
pip install -r requirements.txt
streamlit run app.py
```

После запуска открыть http://localhost:8501
