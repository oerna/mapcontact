#!/bin/bash

# Create a directory for certbot
mkdir -p ~/certbot
cd ~/certbot

# Download certbot-auto
wget https://dl.eff.org/certbot-auto
chmod a+x certbot-auto

# Stop Apache temporarily (using DomainFactory's method)
~/bin/apache2/bin/apachectl stop

# Obtain the certificate
./certbot-auto certonly --standalone -d contactbook.oerna.de

# Start Apache again
~/bin/apache2/bin/apachectl start

# Create a renewal script
cat > ~/renew_ssl.sh << 'EOF'
#!/bin/bash
cd ~/certbot
./certbot-auto renew --quiet
~/bin/apache2/bin/apachectl reload
EOF

chmod +x ~/renew_ssl.sh

# Add to crontab for automatic renewal
(crontab -l 2>/dev/null; echo "0 0 1 * * ~/renew_ssl.sh") | crontab -

echo "SSL installation completed!" 