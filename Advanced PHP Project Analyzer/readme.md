# PHP Project Analyzer

An **AI-ready, scalable code analysis tool** designed to scan PHP projects, extract critical insights, and generate structured summaries. This tool helps developers understand, audit, and query their codebases efficiently.

---

## 🚀 **Features**

- **Deep Code Analysis:** Extracts classes, functions (with parameters), constants, API calls, properties (with visibility), namespaces, includes, and more.
- **Automated Summaries:** Generates detailed project reports in JSON and YAML formats with timestamps.
- **Natural Language Query Ready:** Designed for future integration with AI agents, enabling natural language queries against your codebase.
- **Recursive Directory Scanning:** Processes all PHP files within a specified directory and its subfolders.
- **Debug Mode:** Offers in-depth logs for troubleshooting and development insights.

---

## ⚙️ **Installation**

1. **Clone the Repository:**  
   ```bash
   git clone https://github.com/your-repo/php-project-analyzer.git
   cd php-project-analyzer
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
python workbench.py /path/to/php/project
```

### **With Debug Mode:**  
```bash
python workbench.py /path/to/php/project --debug
```

### **Custom Output Directory:**  
```bash
python workbench.py /path/to/php/project -o custom_output
```

#### **Generated Files:**
- `project_summary.json` - Structured project analysis (JSON format)
- `project_summary.yaml` - Structured project analysis (YAML format)

---

## 🤖 **AI Integration (Coming Soon)**

We are developing an **AI-powered query agent** that allows users to:
- Ask natural language questions like:
  - "Which functions lack PHPDoc comments?"
  - "List all API calls used in the project."
- Get **code quality insights**, **refactoring suggestions**, and **security vulnerability detection**.

Stay tuned for updates as we roll out these AI features!

---

## 📂 **Project Structure**

```
php-project-analyzer/
├── workbench.py          # Main entry script
├── modules/              # Core analysis modules (parser, storage, API)
├── summaries/            # Auto-generated output reports (JSON/YAML)
├── requirements.txt      # Project dependencies
└── README.md             # This documentation
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
- **Email:** dadudekc@gmail.com
- **GitHub Issues:** [Open an Issue](https://github.com/your-repo/php-project-analyzer/issues)

Let’s build the future of code intelligence together. 🚀

