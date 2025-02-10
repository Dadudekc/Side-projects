# Python Project Analyzer

An **AI-ready, scalable code analysis tool** designed to scan Python projects, extract critical insights, and generate structured summaries. This tool helps developers understand, audit, and query their codebases efficiently.

---

## 🚀 **Features**

- **Deep Code Analysis:** Extracts classes, functions (with parameters), constants, API calls, imports, and more.
- **Automated Summaries:** Generates detailed project reports in JSON and YAML formats with timestamps.
- **Natural Language Query Ready:** Designed for future integration with AI agents, enabling natural language queries against your codebase.
- **Recursive Directory Scanning:** Processes all Python files within a specified directory and its subfolders.
- **Debug Mode:** Offers in-depth logs for troubleshooting and development insights.

---

## ⚙️ **Installation**

1. **Clone the Repository:**  
   ```bash
   git clone https://github.com/your-repo/python-project-analyzer.git
   cd python-project-analyzer
   ```

2. **(Optional) Create a Virtual Environment:**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

> **Note:** For YAML support, ensure `PyYAML` is installed:
> ```bash
> pip install pyyaml
> ```

---

## 📊 **Usage**

### **Basic Analysis:**  
```bash
python analyzer.py /path/to/python/project
```

### **With Debug Mode:**  
```bash
python analyzer.py /path/to/python/project --debug
```

### **Custom Output Directory:**  
```bash
python analyzer.py /path/to/python/project -o custom_output
```

#### **Generated Files:**
- `project_summary.json` - Structured project analysis (JSON format)
- `project_summary.yaml` - Structured project analysis (YAML format)

---

## 🤖 **AI Integration (Coming Soon)**

We are developing an **AI-powered query agent** that allows users to:
- Ask natural language questions like:
  - "Which functions lack docstrings?"
  - "List all external API calls in the project."
- Get **code quality insights**, **refactoring suggestions**, and **security vulnerability detection**.

Stay tuned for updates as we roll out these AI features!

---

## 📂 **Project Structure**

```
python-project-analyzer/
├── analyzer.py             # Main entry point: launches the PyQt5 GUI
├── modules/                
│   ├── __init__.py         # (Empty) Makes 'modules' a Python package
│   ├── analyzer_core.py    # Contains the code analysis logic (file scanning, extraction, etc.)
│   ├── db_manager.py       # Manages SQLite connection and CRUD operations
│   └── gui.py              # Implements the PyQt5 GUI interface
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation (includes details below)

```

---

## 🗓️ **Roadmap Highlights**

- ✅ **Phase 1:** Modular Architecture & Database Integration
- 🚀 **Phase 2:** API Development + Async Processing
- 🤖 **Phase 3:** AI Agent for Code Queries
- 🌐 **Phase 4:** Web Dashboard with Visual Analytics
- ☁️ **Phase 5:** Scalable SaaS Deployment

Read the full [Project Roadmap](./ROADMAP.md) for more details.

---

## 🤝 **Contributing**

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m 'Add some awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a pull request

We welcome contributions that improve performance, add features, or enhance AI capabilities.

---

## 📜 **License**

This project is licensed under the [MIT License](./LICENSE).

---

## ✨ **Contact**

For questions, suggestions, or collaboration:
- **Email:** your-email@example.com
- **GitHub Issues:** [Open an Issue](https://github.com/your-repo/python-project-analyzer/issues)

Let’s build the future of code intelligence together. 🚀

