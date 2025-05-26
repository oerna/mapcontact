import os
import subprocess
import shutil

def setup_git():
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Remove existing .git if it exists
    if os.path.exists('.git'):
        print("Removing existing .git directory...")
        shutil.rmtree('.git')
    
    # Initialize new git repository
    print("Initializing new git repository...")
    subprocess.run(['git', 'init'])
    
    # Create post-receive hook
    print("Creating post-receive hook...")
    os.makedirs('.git/hooks', exist_ok=True)
    with open('.git/hooks/post-receive', 'w') as f:
        f.write(f'''#!/bin/bash
TARGET="{current_dir}"
GIT_DIR="{current_dir}/.git"
BRANCH="main"

while read oldrev newrev ref
do
    if [[ $ref = refs/heads/$BRANCH ]];
    then
        echo "Deploying $BRANCH branch..."
        git --work-tree=$TARGET --git-dir=$GIT_DIR checkout -f $BRANCH
        
        # Set up Python virtual environment
        cd $TARGET
        rm -rf venv
        python3 -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Initialize database
        python3.6 init_db.py
        
        # Restart the application
        touch $TARGET/tmp/restart.txt
    else
        echo "Ref $ref received. Doing nothing: only the $BRANCH branch may be deployed on this server."
    fi
done
''')
    
    # Make the hook executable
    os.chmod('.git/hooks/post-receive', 0o755)
    
    # Create initial commit
    print("Creating initial commit...")
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Initial commit'])
    
    print("\nGit repository initialized successfully!")
    print("\nNext steps:")
    print("1. On your local machine, run:")
    print(f"   git remote add production ssh://ddiemeo9zafc@contactbook.oerna.de{current_dir}/.git")
    print("2. Then push your code:")
    print("   git push -f production main")

if __name__ == '__main__':
    setup_git() 