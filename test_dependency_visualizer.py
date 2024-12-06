import unittest
from unittest.mock import patch, MagicMock
from dependency_visualizer import load_config, get_commit_history, generate_dependency_graph

class TestDependencyVisualizer(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_commit_history_empty(self, mock_run):
        """Тест: обработка пустой истории коммитов."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        commits = get_commit_history("/path/to/repo")
        self.assertEqual(commits, [], "Пустая история должна возвращать пустой список.")

    @patch("subprocess.run")
    def test_get_commit_history_valid_data(self, mock_run):
        """Тест: обработка валидной истории коммитов."""
        mock_run.return_value = MagicMock(
            stdout="1234567|abcdef1|2024-12-01|refs/heads/main\n"
                   "abcdef1|789abcd|2024-12-02|\n"
                   "789abcd||2024-12-03|",
            stderr="", returncode=0
        )
        commits = get_commit_history("/path/to/repo")
        expected_commits = [
            {"hash": "1234567", "parents": ["abcdef1"], "date": "2024-12-01", "refs": "refs/heads/main"},
            {"hash": "abcdef1", "parents": ["789abcd"], "date": "2024-12-02", "refs": ""},
            {"hash": "789abcd", "parents": [], "date": "2024-12-03", "refs": ""}
        ]
        self.assertEqual(commits, expected_commits, "История коммитов должна совпадать с ожидаемыми данными.")

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='{"graphviz_path": "dot", "repository_path": "/repo"}')
    def test_load_config_valid(self, mock_open, mock_exists):
        """Тест: загрузка корректного конфигурационного файла."""
        config = load_config("/path/to/config.json")
        self.assertEqual(config["graphviz_path"], "dot")
        self.assertEqual(config["repository_path"], "/repo")

    @patch("subprocess.run")
    def test_get_commit_history_empty(self, mock_run):
        """Тест: обработка пустой истории коммитов."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        commits = get_commit_history("/path/to/repo")
        self.assertEqual(commits, [], "Пустая история должна возвращать пустой список.")


    def test_load_config_missing_file(self):
        """Тест: обработка отсутствующего конфигурационного файла."""
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(SystemExit) as cm:
                load_config("/path/to/invalid_config.json")
            self.assertEqual(cm.exception.code, 1)

    def test_generate_dependency_graph(self):
         """Тест: генерация графа зависимостей коммитов."""
         commits = [
             {"hash": "1234567", "parents": ["abcdef1"], "date": "2024-12-01", "refs": "refs/heads/main"},
             {"hash": "abcdef1", "parents": ["789abcd"], "date": "2024-12-02", "refs": ""},
             {"hash": "789abcd", "parents": [], "date": "2024-12-03", "refs": ""}
         ]
         graph = generate_dependency_graph(commits)
         graph_source = graph.source

         # Проверяем основные элементы графа
         self.assertIn('1234567', graph_source)  # Идентификатор коммита
         self.assertIn('abcdef1', graph_source)  # Родительский коммит
         self.assertIn('789abcd', graph_source)  # Ещё один коммит
         self.assertIn('refs/heads/main', graph_source)  # Ссылка на ветку
         self.assertIn('1234567\\n2024-12-01', graph_source)  # Дата коммита
         self.assertIn('abcdef1 -> 1234567', graph_source)  # Связь между коммитами




if __name__ == "__main__":
    unittest.main()
