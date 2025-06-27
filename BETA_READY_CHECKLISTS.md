# Beta-Ready Checklists

This file consolidates the required components, tests, and validations each side project must complete before a beta release.

## VlogForge
- [ ] Core modules implemented and unit tested
- [ ] UI modules functional with basic tests
- [ ] API integrations configured with `.env` examples
- [ ] `verify_beta.py` run and report reviewed

## AI Architect
- [ ] FastAPI endpoints return valid projects
- [ ] Code generator and self-evolver tested
- [ ] Bootstrap and deployment scripts execute without errors
- [ ] CI pipeline runs unit tests automatically

## API Wizard
- [ ] Basic Flask wizard flows work end-to-end
- [ ] Automation scripts tested with at least one API
- [ ] Celery worker handles tasks reliably
- [ ] Documentation covers setup and troubleshooting

## SkillSwap
- [ ] User onboarding, matching, chat and feedback implemented
- [ ] Point wallet and safety features deployed
- [ ] Load tests and QA pass on staging

## Trading System Optimizer
- [ ] Trade entry GUI logs to YAML correctly
- [ ] Analytics modules generate equity curves
- [ ] Discord notifications send successfully
- [ ] Unit tests for analytics and bot modules pass

## GUI Task Managers
- [ ] Tasks persist to `tasks.json` or CSV
- [ ] Basic filtering and progress indicators work
- [ ] Tests in `tests/test_tasks_json.py` pass

These checklists prioritize core functionality and testing over perfection so the projects can be shipped for beta evaluation.
