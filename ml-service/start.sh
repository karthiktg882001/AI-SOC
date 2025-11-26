#!/bin/bash
# Don't exit on error - let uvicorn handle errors
set +e

echo "🚀 Starting ML Service..."
echo "Working directory: $(pwd)"
echo "Python: $(which python)"

# Start uvicorn - use exec to replace shell process
# This ensures uvicorn runs as PID 1 and stays alive
echo "🌐 Starting uvicorn server on 0.0.0.0:8000..."
echo "📡 Server will listen on http://0.0.0.0:8000"

# Use uvicorn with explicit configuration
exec python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    --timeout-keep-alive 30 \
    --access-log \
    --no-use-colors

