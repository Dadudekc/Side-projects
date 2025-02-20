import subprocess

def run_linters():
    """Runs Ruff, Black, and Pylint for AI-driven linting and formatting."""
    print("🔍 Running Black (Auto-format)...")
    subprocess.run(["black", "."])

    print("🔍 Running Ruff (Linting)...")
    subprocess.run(["ruff", "check", "."])

    print("🔍 Running Pylint (Static Analysis)...")
    subprocess.run(["pylint", "--disable=C0114,C0116", "."])

if __name__ == "__main__":
    run_linters()
