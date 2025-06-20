# Side Projects

A collection of experimental Python projects ranging from social media automation to small API and GUI utilities.  Each folder acts as a standalone mini project with its own focus.  This repository groups them together for exploration and learning purposes.

## Projects

### VlogForge (`Forges/VlogForge`)
Content automation toolkit with multiple modules for managing social media workflows.  Features include:

- API integrations for Mailchimp, Twitter, and YouTube
- Core utilities for A/B testing, caption suggestions, audience tracking and more
- Example workflow in `main.py`
- Unit tests covering content management and engagement tracking

Install dependencies and run tests:

```bash
pip install -r Forges/VlogForge/requirements.txt
pytest Forges/VlogForge/tests
```

Some tests that rely on Mailchimp credentials are skipped in this repo.

### AI Architect (`Wizards/AI_Architect`)
Prototype FastAPI application that can generate small pieces of Python code and experiment with "self‑evolving" analysis.

Key modules are under `app/` with tests in `tests/`.
Run the sample tests with:

```bash
pytest Wizards/AI_Architect/tests
```

### API Wizard (`Wizards/api_wizard_project`)
Tiny example showing a simple `APIWizard` class.  Minimal tests live under `tests/`.

### GUI Task Managers
Two desktop utilities for personal task tracking:

- `task_manager.py` – PyQt based interface
- `tkinter_workflow_manager.py` – Tkinter based manager that saves tasks to `tasks.json`

A small test in `tests/test_tasks_json.py` verifies that `tasks.json` is present and formatted correctly.

## Project Structure

```
Forges/              Social‑media automation tools
Wizards/             Assorted API and FastAPI experiments
data/                Example CSV data files
tasks.json           Saved tasks for the Tkinter workflow manager
```

## Running Tests

After installing Python 3.12+ and installing dependencies for individual projects, run tests with `pytest`:

```bash
pytest
```

This executes the lightweight tests included with each subproject.  Tests requiring external APIs or credentials are omitted by default.

## License

This repository is licensed under the MIT License.  See [LICENSE](LICENSE) for details.
