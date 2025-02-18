import os

base_path = "D:\\side_projects\\Side-projects\\ai_agent_project\\ai_engine\\models\\debugger"
output_file = "debugger_files_summary.txt"

def extract_code_snippets():
    with open(output_file, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    out.write(f"\n{'='*80}\n📌 {file_path}\n{'='*80}\n")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            snippet = "".join(lines[:50])  # First 50 lines for context
                            out.write(snippet + "\n")
                    except Exception as e:
                        out.write(f"Error reading {file}: {e}\n")

if __name__ == "__main__":
    extract_code_snippets()
    print(f"✅ Debugger file summaries saved to: {output_file}")
