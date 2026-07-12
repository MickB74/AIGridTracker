#!/bin/bash
# Double-click to STOP the last running session and RESTART the app,
# then open it in your browser.
cd "$(dirname "$0")" || exit 1

PORT=8520

# 1) Stop the last session — kill whatever is holding our port.
STUCK_PIDS=$(lsof -ti "tcp:$PORT" 2>/dev/null)
if [ -n "$STUCK_PIDS" ]; then
    echo "Stopping previous session on port $PORT (PID(s): $STUCK_PIDS) …"
    echo "$STUCK_PIDS" | xargs kill -9 2>/dev/null
    sleep 1
else
    echo "No previous session on port $PORT."
fi

# 2) Pick an interpreter: local .venv if present, else system streamlit.
if [ -x ".venv/bin/streamlit" ]; then
    STREAMLIT=".venv/bin/streamlit"
else
    STREAMLIT="$(command -v streamlit)"
fi
if [ -z "$STREAMLIT" ]; then
    echo "streamlit not found. Run: pip install -r requirements.txt"
    exit 1
fi

# 3) Open the browser once Streamlit has had a moment to bind the port.
(sleep 3 && open "http://localhost:$PORT") &

# 4) Restart (foreground; close this window or Ctrl-C to stop).
echo "Starting GridWatch AI on http://localhost:$PORT …"
exec "$STREAMLIT" run app.py \
    --server.port "$PORT" \
    --server.headless false
