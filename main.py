import ast
import sys
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def read_source(path):

    """ Read the file """

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# encoding="utf-8" — always be explicit; Windows defaults to cp1252 and will choke on emoji/comments. This is also the latest standard after 3.15
def parse(source):
    return ast.parse(source)

# tree = parse(read_source("sample.py"))
# print(type(tree))

# Python already reads your code to run it. ast.parse() gives you the same structure Python builds internally, 
# as plain Python objects you can walk around.
#  It's not magic — it's Python exposing its own guts.

def find_functions(tree):

    """ Find functions traversing the tree """

    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            funcs.append(node)
    return funcs

def function_info(node):

    """ Find function description from traversing node""" 

    # List comprehension: [a.arg for a in node.args.args] — reads left to right as "give me a.arg for each a in the list."

    arg_names = [a.arg for a in node.args.args]
    return {
        "name": node.name,
        "args": arg_names,
        "lineno": node.lineno,
        "end_lineno": node.end_lineno,
    }



def longest_function(func_infos):

    """ Finds the longest function in the tree """

    if not func_infos:
        return None
    return max(func_infos, key=lambda f: f["end_lineno"] - f["lineno"])



def find_imports(tree):
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    return imports



# The raw version

# source = parse(read_source("sample.py"))
# # print(len(source), "characters")
# # print(source[:50])
# #print(ast.dump(tree, indent=2))
# for fn in find_functions(source):
#     print(fn.name, "at line", fn.lineno)
#     print(function_info(fn))

# infos = [function_info(fn) for fn in find_functions(tree)]  
# print(longest_function(infos))

# print(find_imports(source))


# Report Generation
def print_report(path, source, func_infos, imports):
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    print(f"-------- Analysis: {path} --------")
    print(f"Lines of code: {len(lines)}")
    print(f"Functions found: {len(func_infos)}")
    for f in func_infos:
        args = ", ".join(f["args"])
        print(f" - {f['name']}({args})")
    longest = longest_function(func_infos)

    if longest: 
        length = longest["end_lineno"] - longest["lineno"] + 1
        print(f"Longest function:  {longest['name']} ({length} lines)")
    print(f"Imports: {','.join(imports)}")


def build_report(path, source, func_infos, imports):
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    report = []
    report.append(f"=== Analysis: {path} ===")
    report.append(f"Lines of code:    {len(lines)}")
    report.append(f"Functions found:  {len(func_infos)}")
    for f in func_infos:
        args = ", ".join(f["args"])
        report.append(f"  - {f['name']}({args})")
    longest = longest_function(func_infos)
    if longest:
        length = longest["end_lineno"] - longest["lineno"] + 1
        report.append(f"Longest function: {longest['name']} ({length} lines)")
    report.append(f"Imports:          {', '.join(imports)}")
    return "\n".join(report)


SYSTEM_PROMPT = """You are a senior Python code reviewer, in the style of CodeRabbit. You review a single file at a time and report only issues that matter.

## Inputs
- `report`: a static analysis summary — lines of code, functions with their argument names, the longest function, and imports.
- `source`: the full source of the file being reviewed.

## What to look for, in priority order
1. **Correctness** — bugs, unhandled exceptions, off-by-one errors, mutable default arguments, shadowed names, unreachable code.
2. **Function design** — functions with more than 4 parameters, functions doing more than one thing, functions that are very long relative to the file, missing or misleading names.
3. **Readability** — deep nesting, dead code, commented-out code, missing docstrings on non-trivial functions, inconsistent style.

## Output format
Return plain text, no markdown headers, no code fences. Structure:

REVIEW
- <finding 1>
- <finding 2>
- <finding 3>

RISK: LOW | MEDIUM | HIGH

## Rules
- 3 to 5 findings. Never more, never fewer.
- Each finding: one or two sentences. Name the function or line.
- Reference the static report only when it reveals something the code alone doesn't (e.g. "process_data has 4 parameters").
- Do not suggest adding type hints, tests, or tooling unless the code has an actual bug that those would catch.
- Do not suggest rewriting the file. Small, local fixes only.
- If there is nothing wrong, output a single finding: "No significant issues found." and set RISK: LOW.
- Never invent a problem to fill the list.

## Tone
Direct and specific. No praise, no filler, no "great job". A reviewer who says nothing when nothing is wrong is more useful than one who pads.
"""

#AI Analyze
def analyze_with_gemini(report_text, source_code):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable not set."

    client = genai.Client(api_key=api_key)  

    prompt = f"""You are a code reviewer like CodeRabbit... 
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",           
        config = {
            "system_instruction" : SYSTEM_PROMPT,
        },
        contents=f"Static analysis report:\n{report_text}\n\nSource code:\n```python\n{source_code}\n```",
    )
    return response.text

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python codecheck.py <file.py>")
#         sys.exit(1)
#     path = sys.argv[1]
#     source = read_source(path)
#     tree = parse(source)
#     func_infos = [function_info(fn) for fn in find_functions(tree)]
#     imports = find_imports(tree)
#     print_report(path, source, func_infos, imports)


def main():
    if len(sys.argv) < 2:
        print("Usage: python codecheck.py <file.py> [--ai]")
        sys.exit(1)
    
    path = sys.argv[1]
    use_ai = "--ai" in sys.argv
    
    source = read_source(path)
    tree = parse(source)
    func_infos = [function_info(fn) for fn in find_functions(tree)]
    imports = find_imports(tree)
    
    report = build_report(path, source, func_infos, imports)
    print(report)
    
    if use_ai:
        print("\n=== AI Review ===")
        print(analyze_with_gemini(report, source))

if __name__ == "__main__":
    main()