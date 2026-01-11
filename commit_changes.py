import subprocess
import os

os.chdir(r'd:\CODEX\DUMPTOOLS')
env = os.environ.copy()
env['GIT_PAGER'] = ''

# Check status
result = subprocess.run(['git', 'status', '--short'], env=env, capture_output=True, text=True)
print("Git status:")
print(result.stdout)

# If there are changes, commit them
if result.stdout.strip():
    print("\nCommitting changes...")
    result = subprocess.run([
        'git', 'add', '-A'
    ], env=env, capture_output=True, text=True)
    
    result = subprocess.run([
        'git', 'commit', '-m', 'Add URL file loader and bulk URL vulnerability scanner'
    ], env=env, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
else:
    print("No changes to commit")

# Show last commit
print("\nLast commits:")
result = subprocess.run(['git', 'log', '--oneline', '-3'], env=env, capture_output=True, text=True)
print(result.stdout)
