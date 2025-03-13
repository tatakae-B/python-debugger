from flask import Flask, render_template, request, jsonify
import ast
import traceback

app = Flask(__name__)

# Function to check syntax errors
def check_syntax(code):
    try:
        ast.parse(code)
        return None  # No syntax errors
    except SyntaxError as e:
        return f"Syntax Error: {e.msg} at line {e.lineno}"

# Function to auto-fix common syntax issues
def auto_fix_code(code):
    lines = code.strip().split("\n")
    fixed_lines = []

    # Stack to track unclosed brackets and quotes
    open_symbols = {"(": ")", "[": "]", "{": "}"}
    stack = []
    unclosed_string = None

    for line in lines:
        stripped_line = line.strip()

        # Fix missing colons for loops and conditions
        if stripped_line.startswith(("if ", "elif ", "for ", "while ", "def ", "class ")) and not stripped_line.endswith(":"):
            stripped_line += ":"

        # Track opening symbols
        for char in stripped_line:
            if char in open_symbols:
                stack.append(open_symbols[char])
            elif stack and char == stack[-1]:
                stack.pop()

        # Handle unclosed string literals
        if stripped_line.count('"') % 2 != 0:
            stripped_line += '"'
        if stripped_line.count("'") % 2 != 0:
            stripped_line += "'"

        fixed_lines.append(stripped_line)

    # Ensure unclosed brackets are closed
    while stack:
        fixed_lines[-1] += stack.pop()

    return "\n".join(fixed_lines)

# Function to check runtime errors
def check_runtime_errors(code):
    try:
        exec(code, {}, {})
        return None  # No runtime errors
    except Exception as e:
        return f"Runtime Error:\n{traceback.format_exc()}"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/debug', methods=['POST'])
def debug_code():
    code = request.json.get("code", "").strip()

    # Check syntax errors
    syntax_error = check_syntax(code)
    if syntax_error:
        fixed_code = auto_fix_code(code)
        return jsonify({"error": syntax_error, "fixed_code": fixed_code, "message": "✅ Auto-fixed syntax error!"})

    # Check runtime errors
    runtime_error = check_runtime_errors(code)
    if runtime_error:
        return jsonify({"error": runtime_error, "fixed_code": code, "message": "⚠️ Runtime error detected, check the code!"})

    return jsonify({"message": "✅ No errors found! Your code is correct.", "fixed_code": code})

if __name__ == '__main__':
    app.run(debug=True)
