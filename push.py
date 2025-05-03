import subprocess


# Function to run git commands and check for errors
def run_git_command(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

# Get commit message
commit_msg = input("Enter commit message: ").strip()

# Check if commit message is empty
if not commit_msg:
    print("Error: Commit message cannot be empty!")
    exit(1)

# Add all changes to staging
if not run_git_command("git add ."):
    exit(1)

# Commit changes
if not run_git_command(f'git commit -m "{commit_msg}"'):
    exit(1)

# Prompt to push to GitHub
if input("Push to GitHub? (Y/n): ").strip().lower() == "y":
    if not run_git_command("git push origin main"):
        exit(1)

print("Git operations completed successfully.")
