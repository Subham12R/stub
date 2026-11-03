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



def main():
    if len(sys.argv) != 2:
        print("Usage: python codecheck.py <file.py>")
        sys.exit(1)
    path = sys.argv[1]
    source = read_source(path)
    tree = parse(source)
    func_infos = [function_info(fn) for fn in find_functions(tree)]
    imports = find_imports(tree)
    print_report(path, source, func_infos, imports)



if __name__ == "__main__":
    main()