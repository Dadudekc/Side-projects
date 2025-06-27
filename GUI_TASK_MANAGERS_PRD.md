# GUI Task Managers Product Requirements Document

## Purpose
Two small desktop utilities help users track tasks. The PyQt version (`task_manager.py`) offers a rich table view, while the Tkinter version (`tkinter_workflow_manager.py`) saves tasks to `tasks.json`.

## Target Users
- Individuals needing lightweight personal task tracking

## Features
- Add, edit and remove tasks
- Persistence to JSON or CSV
- Basic progress indicators
- Simple filtering and sorting

## Success Metrics
- Tasks persist across sessions
- UI loads without errors
- `tests/test_tasks_json.py` passes
