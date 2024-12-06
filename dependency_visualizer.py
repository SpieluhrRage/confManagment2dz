import os
import sys
import json
import subprocess
from graphviz import Digraph
import re
import unittest

def load_config(config_path):
    """
    Загружает конфигурационный файл в формате JSON.
    """
    if not os.path.exists(config_path):
        print(f"Конфигурационный файл '{config_path}' не найден.")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе конфигурационного файла: {e}")
        sys.exit(1)

    required_keys = ['graphviz_path', 'repository_path']
    for key in required_keys:
        if key not in config:
            print(f"Отсутствует ключ '{key}' в конфигурационном файле.")
            sys.exit(1)
    
    if not os.path.exists(config['graphviz_path']):
        print(f"Graphviz не найден по пути '{config['graphviz_path']}'.")
        sys.exit(1)
    
    if not os.path.exists(config['repository_path']):
        print(f"Репозиторий не найден по пути '{config['repository_path']}'.")
        sys.exit(1)
    
    return config

def get_commit_history(repo_path):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'log', '--all', '--pretty=format:%H|%P|%ad|%D', '--date=short'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении git команды: {e.stderr}")
        sys.exit(1)
    
    commits = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():  # Пропускаем пустые строки
            continue
        parts = line.split('|')
        commit_hash = parts[0]
        parents = parts[1].split() if len(parts) > 1 and parts[1] else []
        date = parts[2] if len(parts) > 2 else ""
        refs = parts[3] if len(parts) > 3 else ""
        commits.append({'hash': commit_hash, 'parents': parents, 'date': date, 'refs': refs})
    
    return commits


def generate_dependency_graph(commits):
    """
    Генерирует граф зависимостей коммитов с учетом ветвей и дат.
    """
    graph = Digraph(comment='Commit Dependency Graph')
    graph.attr('node', shape='ellipse', fontsize='10')
    
    for commit in commits:
        label = f"{commit['hash'][:7]}\\n{commit['date']}"
        if commit['refs']:
            label += f"\\n({commit['refs']})"
        graph.node(commit['hash'], label=label)
    
    for commit in commits:
        for parent in commit['parents']:
            graph.edge(parent, commit['hash'])
    
    return graph

def render_graph(graph, graphviz_path):
    """
    Рендерит граф с использованием Graphviz и открывает его.
    """
    output_path = 'commit_dependency_graph'
    graph.render(output_path, format='png', cleanup=True)
    image_path = f"{output_path}.png"
    
    if not os.path.exists(image_path):
        print("Ошибка: Не удалось создать изображение графа.")
        sys.exit(1)
    
    # Открываем созданное изображение с помощью системной программы
    try:
        if sys.platform == "win32":
            os.startfile(image_path)  # Windows
        elif sys.platform == "darwin":
            subprocess.run(["open", image_path], check=True)  # macOS
        else:
            subprocess.run(["xdg-open", image_path], check=True)  # Linux
    except Exception as e:
        print(f"Ошибка при открытии изображения: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Использование: python dependency_visualizer.py <config.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    config = load_config(config_path)
    
    repo_path = config['repository_path']
    graphviz_path = config['graphviz_path']
    
    commits = get_commit_history(repo_path)
    if not commits:
        print("Нет коммитов для отображения.")
        sys.exit(0)
    
    graph = generate_dependency_graph(commits)
    render_graph(graph, graphviz_path)
    print("Граф зависимостей успешно создан и открыт.")

if __name__ == "__main__":
    main()
