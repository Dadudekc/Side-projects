import subprocess

SCRIPTS = [
    "fix_imports.py",
    "fix_strings.py",
    "fix_parentheses.py",
    "fix_indentation.py",
    "fix_syntax.py"
]

def run_script(script):
    print(f"🚀 Running {script}...")
    subprocess.run(["python", script], check=True)

def run_all_fixes():
    for script in SCRIPTS:
        run_script(script)

    print("\n🚀 Running tests to verify fixes...")
    subprocess.run(["pytest", "tests/"], check=False)

if __name__ == "__main__":
    run_all_fixes()
