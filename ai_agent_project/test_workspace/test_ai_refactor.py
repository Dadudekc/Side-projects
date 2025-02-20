import os
from ai_refactor_agent import analyze_code_with_ollama

def test_ai_refactoring():
    test_file = "dummy_test.py"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("print('Test AI refactor')")
    original_code, ai_suggestion = analyze_code_with_ollama(test_file)
    assert ai_suggestion is not None, "❌ AI refactor returned no result."
    print("✅ AI refactoring test passed!")

if __name__ == "__main__":
    test_ai_refactoring()
