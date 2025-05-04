import os
import re
import subprocess
import sys
import pathspec
from importlib import metadata


def find_imports_in_file(file_path):
    """Find all import statements in a Python file."""
    import_statements = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Match `import package`
        matches = re.findall(r'^\s*import (\w+)', content, re.MULTILINE)
        import_statements.update([match for match in matches if not match in sys.stdlib_module_names and not match.startswith("_")])

        # Match `from package import ...`
        matches = re.findall(r'^\s*from (\w+) import', content, re.MULTILINE)
        import_statements.update([match for match in matches if not match in sys.stdlib_module_names and not match.startswith("_")])

    return import_statements


def get_local_modules(project_path, gitignore_spec=None):
    """Find top-level Python files and packages (with __init__.py) in the actual project folder.
    """
    local_modules = set()
    for root, dirs, files in os.walk(project_path):
        if gitignore_spec.match_file(root):
            continue
        for file in files:
            if file.endswith('.py'):
                local_modules.add(file[:-3])
        for dir_name in dirs:
            if os.path.exists(os.path.join(root, dir_name, '__init__.py')):
                local_modules.add(dir_name)
    return local_modules


def load_gitignore_spec(project_path):
    """Load .gitignore rules using pathspec."""
    gitignore_path = os.path.join(project_path, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            lines = f.read().splitlines()
            return pathspec.PathSpec.from_lines('gitwildmatch', lines)
    return None


def find_all_python_files(project_path, gitignore_spec=None):
    """Recursively find all Python files, skipping .gitignore rules."""
    python_files = []
    for root, dirs, files in os.walk(project_path):
        rel_root = os.path.relpath(root, project_path)

        # Skip ignored folders
        dirs[:] = [d for d in dirs if not (
            gitignore_spec and gitignore_spec.match_file(os.path.join(rel_root, d))
        )]

        for file in files:
            rel_file_path = os.path.join(rel_root, file)
            if file.endswith('.py') and not (
                gitignore_spec and gitignore_spec.match_file(rel_file_path)
            ):
                full_path = os.path.join(root, file)
                python_files.append(full_path)

    return python_files


def get_missing_packages(packages):
    """Check which packages are not installed and are not part of the standard library."""
    stdlib_modules = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
    missing_packages = []
    for package in packages:
        if package in stdlib_modules:
            continue
        try:
            subprocess.run(['python3', '-c', f'import {package}'],
                           check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            missing_packages.append(package)
    return missing_packages


def main(project_path):
    """Main function to extract imports and check dependencies."""
    project_path = os.path.expanduser(project_path)
    all_imports = set()

    # Step 1: Load .gitignore (if exists)
    gitignore_spec = load_gitignore_spec(project_path)

    # Step 2: Find all .py files (ignoring .gitignore)
    python_files = find_all_python_files(project_path, gitignore_spec)

    # Step 3: Extract import statements
    for file_path in python_files:
        file_imports = find_imports_in_file(file_path)
        all_imports.update(file_imports)

    # Step 3.5: Exclude local project modules
    local_modules = get_local_modules(project_path, gitignore_spec)
    all_imports -= local_modules

    # Step 4: Check which are missing
    missing_packages = get_missing_packages(all_imports)

    # Step 5: Output results
    print(f"\n📦 Found imports: ")
    for pkg in sorted(all_imports):
        print(f"  - {pkg}")
    if missing_packages:
        print("\n❌ Missing packages (not installed):")
        for pkg in missing_packages:
            print(f"  - {pkg}")
    else:
        print("\n✅ All required packages are installed!")

    # Step 6: Write requirements.txt
    with open('requirements.txt', 'w') as req_file:
        for package in sorted(all_imports):
            if package not in sys.stdlib_module_names:
                try:
                    version = metadata.version(package)
                    req_file.write(f"{package}~={version}\n")
                except metadata.PackageNotFoundError:
                    print(f"⚠️  Warning: Version for '{package}' not found, skipping.")

    print("\n📝 requirements.txt generated.")


if __name__ == '__main__':
    main("~/PycharmProjects/NebulaOS Restart/")
