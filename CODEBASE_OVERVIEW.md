# Codebase Overview

This repository contains several unrelated prototypes.  The table below lists the major directories and their purpose.

| Path | Description |
| ---- | ----------- |
| `Forges/VlogForge` | Social media automation toolkit with many submodules and example workflow in `main.py`. Includes unit tests in `tests/`. |
| `Wizards/AI_Architect` | FastAPI based experiment for code generation and self-evolving suggestions. Tests live under `tests/`. |
| `Wizards/api_wizard_project` | Minimal example with an `APIWizard` class. |
| `data/` | CSV files used by VlogForge modules. |
| `tasks.json` | Data file for the Tkinter workflow manager. |
| `tests/` | Simple tests for shared assets such as `tasks.json`. |

Each subproject may have its own dependency list.  `Forges/VlogForge/requirements.txt` is the most complete example and includes packages like `requests`, `pandas`, and `scipy`.
