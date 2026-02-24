#!/bin/bash
# Local development server for a11ybob.com
# Serves the site at http://localhost:8000

PORT=${1:-8000}
DIR="$(dirname "$0")/a11ybob.com"

echo "Serving a11ybob.com at http://localhost:${PORT}"
echo "Press Ctrl+C to stop."
python3 -m http.server "$PORT" --directory "$DIR"
