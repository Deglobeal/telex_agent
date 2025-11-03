# deploy.sh
#!/bin/bash
echo "Deploying Telex Code Helper Agent..."

# Install dependencies
pip install -r requirements.txt

# Start the application
gunicorn --bind 0.0.0.0:$PORT wsgi:app --access-logfile - --error-logfile -