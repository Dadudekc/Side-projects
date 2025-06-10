def generate_code(template, **kwargs):
    """Generate code based on a template and provided keyword arguments."""
    return template.format(**kwargs)

if __name__ == "__main__":
    template = "def {function_name}():\n    return {return_value}"
    print(generate_code(template, function_name="hello", return_value="'world'"))
