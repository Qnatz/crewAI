import re
import json

def parse_pipdeptree_output(file_content):
    """
    Parses pipdeptree output to extract top-level packages and their versions.
    """
    top_level_packages = {}
    lines = file_content.splitlines()

    for line in lines:
        # Top-level packages are those that don't start with tree prefixes
        # like '├── ', '│   ', '└── ', etc.
        # A simple check is if the line starts with a character that's part of a package name.
        # pipdeptree output format for top-level is "package_name==version"
        # Sometimes there can be warnings or other text, so we need to be specific.
        match = re.match(r"^([a-zA-Z0-9_-]+)==([a-zA-Z0-9.]+)", line)
        if match:
            package_name = match.group(1)
            version = match.group(2)
            top_level_packages[package_name.lower()] = version

    return top_level_packages

if __name__ == "__main__":
    try:
        with open("full_tree.txt", "r", encoding="utf-8") as f:
            content = f.read()

        parsed_packages = parse_pipdeptree_output(content)
        print(json.dumps(parsed_packages, indent=2))

    except FileNotFoundError:
        print(json.dumps({"error": "full_tree.txt not found"}, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
