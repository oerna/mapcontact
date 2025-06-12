#!/bin/bash

# Remove existing Git repository if it exists
ssh ddiemeo9zafc@contactbook.oerna.de "cd /home/ddiemeo9zafc/mapcontacts && rm -rf .git"

# Initialize new Git repository
ssh ddiemeo9zafc@contactbook.oerna.de "cd /home/ddiemeo9zafc/mapcontacts && git init --bare"

# Create post-receive hook
ssh ddiemeo9zafc@contactbook.oerna.de "cat > /home/ddiemeo9zafc/mapcontacts/.git/hooks/post-receive << 'EOF'
#!/bin/bash
TARGET=\"/home/ddiemeo9zafc/mapcontacts\"
GIT_DIR=\"/home/ddiemeo9zafc/mapcontacts/.git\"
BRANCH=\"main\"

while read oldrev newrev ref
do
    if [[ \$ref = refs/heads/\$BRANCH ]];
    then
        echo \"Deploying \$BRANCH branch...\"
        git --work-tree=\$TARGET --git-dir=\$GIT_DIR checkout -f \$BRANCH
        
        # Set up Python 3.9 virtual environment
        cd \$TARGET
        rm -rf venv
        python3.9 -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Initialize database if needed
        python init_db.py
        
        # Restart the application
        touch \$TARGET/tmp/restart.txt
    else
        echo \"Ref \$ref received. Doing nothing: only the \$BRANCH branch may be deployed on this server.\"
    fi
done
EOF"

# Make the hook executable
ssh ddiemeo9zafc@contactbook.oerna.de "chmod +x /home/ddiemeo9zafc/mapcontacts/.git/hooks/post-receive" 