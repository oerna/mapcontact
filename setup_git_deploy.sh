#!/bin/bash

# Configuration
REMOTE_USER="ddiemeo9zafc"
REMOTE_HOST="contactbook.oerna.de"
REMOTE_DIR="/home/ddiemeo9zafc/mapcontacts"
GIT_REPO="/home/ddiemeo9zafc/git/mapcontacts.git"

# Create Git repository on server
echo "Setting up Git repository on server..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $GIT_REPO && cd $GIT_REPO && git init --bare"

# Add server as remote
echo "Adding server as remote..."
git remote add production $REMOTE_USER@$REMOTE_HOST:$GIT_REPO

# Create post-receive hook
echo "Creating post-receive hook..."
cat > post-receive << 'EOF'
#!/bin/bash
TARGET="/home/ddiemeo9zafc/mapcontacts"
GIT_DIR="/home/ddiemeo9zafc/git/mapcontacts.git"
BRANCH="main"

while read oldrev newrev ref
do
    # Only deploy if we're pushing to main branch
    if [[ $ref = refs/heads/$BRANCH ]];
    then
        echo "Deploying $BRANCH branch..."
        git --work-tree=$TARGET --git-dir=$GIT_DIR checkout -f $BRANCH
        cd $TARGET

        # Create required directories
        mkdir -p $TARGET/logs
        mkdir -p $TARGET/instance
        mkdir -p $TARGET/public

        # Install dependencies using Python 3.7
        echo "Installing dependencies..."
        python3.7 -m pip install --user -r requirements.txt

        # Set permissions
        chmod -R 755 $TARGET
        chmod -R 755 $TARGET/static
        chmod -R 755 $TARGET/public
        chmod -R 755 $TARGET/logs
        chmod -R 755 $TARGET/instance

        # Ensure static files are properly linked
        if [ ! -L "$TARGET/public/static" ]; then
            ln -sf $TARGET/static $TARGET/public/static
        fi

        # Copy .htaccess files
        cp $TARGET/.htaccess $TARGET/public/.htaccess

        # Initialize database
        echo "Initializing database..."
        python3.7 migrate_db.py

        # Restart application
        touch app_wsgi.py
        echo "Deployment completed!"
    fi
done
EOF

# Make post-receive hook executable
chmod +x post-receive

# Upload post-receive hook to server
echo "Uploading post-receive hook..."
scp post-receive $REMOTE_USER@$REMOTE_HOST:$GIT_REPO/hooks/

# Clean up
rm post-receive

echo "Git deployment setup complete!"
echo "You can now deploy changes using: git push production main" 