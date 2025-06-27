# AI Architect Product Requirements Document

## Purpose
AI Architect is a FastAPI application that generates small Python projects and can improve its own code. It aims to accelerate prototyping for developers through automated scaffolding and self‑evolving suggestions.

## Target Users
- Developers who need quick project setups
- Experimenters exploring AI‑driven code generation

## Features
- REST API for project creation and self‑improvement triggers
- Code generator that interfaces with AI models
- Self evolver module to analyze and enhance generated projects
- Test runner for automated validation
- Automation scripts for bootstrapping and deployment

## Success Metrics
- API endpoints respond with valid project structures
- Generated projects pass included unit tests
- Self improvement cycle runs without errors

## Out of Scope
- Production‑grade security or user authentication
- Large language model hosting – relies on external API

## Dependencies
- Python 3.12+
- FastAPI, any AI API keys
