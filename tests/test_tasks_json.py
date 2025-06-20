import json
import os


def test_tasks_file_exists_and_not_empty():
    assert os.path.exists('tasks.json'), "tasks.json should exist"
    with open('tasks.json') as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) > 0, "tasks.json should contain tasks"
