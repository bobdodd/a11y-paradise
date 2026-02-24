#!/bin/bash
# Local development server for a11ybob.com (Flask)
# Serves the site at http://localhost:5000

DIR="$(cd "$(dirname "$0")/a11ybob.com" && pwd)"

# Activate virtual environment
source "$DIR/.venv/bin/activate"

echo "Starting A11y Paradise at http://localhost:5000"
echo "Press Ctrl+C to stop."
cd "$DIR" && flask run
