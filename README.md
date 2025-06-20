# Side Projects by Victor

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

This repository collects a handful of automation experiments built with Python. The flagship project is **VlogForge**, a toolkit for automating social media content. Under **Wizards** you'll find smaller prototypes and code generation helpers. Two task manager GUIs round out the portfolio.

## Projects
- **VlogForge** – generates video scripts, schedules posts and tracks engagement across platforms.
- **Wizards** – assorted experiments such as API signup automation and scaffolds produced by LLMs.
- **Task Managers** – simple PyQt and Tkinter apps for organizing tasks (`task_manager.py` and `tkinter_workflow_manager.py`).

## File Structure
```text
Side-projects/
├── Forges/
│   └── VlogForge/
│       ├── api_intergrations/
│       │   ├── mailchimp_api.py
│       │   └── ...
│       ├── core/
│       │   ├── engagement_tracker.py
│       │   ├── auto_posting.py
│       │   └── ...
│       ├── data/
│       ├── ui/
│       │   ├── content_calendar.py
│       │   └── main_window.py
│       ├── tests/
│       └── main.py
├── Wizards/
│   ├── AI_Architect/
│   └── api_wizard_project/
├── data/
├── drafts.txt
├── task_manager.py
├── tkinter_workflow_manager.py
├── tasks.json
└── interview_summary.txt
```

## Setup
1. Install dependencies for VlogForge:
   ```bash
   pip install -r Forges/VlogForge/requirements.txt
   ```
2. Optional: install additional requirements for other prototypes as needed.
3. Some tests rely on optional packages (`mailchimp_marketing`, `pandas`, `requests`). Install them if you plan to run the full test suite.

## Usage
- **Run the VlogForge demo**
  ```bash
  python Forges/VlogForge/main.py
  ```
- **PyQt task manager**
  ```bash
  python task_manager.py
  ```
- **Tkinter workflow manager**
  ```bash
  python tkinter_workflow_manager.py
  ```

## Key Features
- Script and caption generation via simple LLM prompts
- Auto-post scheduling and audience tracking
- A/B testing utilities and engagement heatmaps
- Early prototypes for self-building project scaffolds

## Architecture
VlogForge is organized into three layers:
1. **API Integrations** – wrappers for services like Mailchimp and Twitter.
2. **Core Modules** – analytics and content management logic.
3. **UI Layer** – optional windows for planning posts and reviewing reports.
Tests cover critical modules, but require the optional dependencies listed above.

## What This Demonstrates
- Modular Python design and separation of concerns
- Integration with external APIs and asynchronous tasks
- Willingness to test and iterate with small prototypes

## License
MIT. See [LICENSE](LICENSE) for details.
