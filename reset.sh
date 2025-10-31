#!/bin/bash

# config
LOG_FILE="Logs"
FRONTIER="frontier.shelve.db"
SESSION_NAME="crawler"
ACTIVATE_VENV="source .venv/bin/activate"
LAUNCH_CMD="python3.12 launch.py"
USAGE="\
USAGE:
  ./reset.sh [OPTIONS]

OPTIONS:
  -r    Remove crawler state and logs (reset)
  -S    Start crawler in a detached tmux session
  -k    Kill all running crawler processes
  -h    Show this help message
"

# flags
DO_LAUNCH="false"
DO_CLEANUP="false"
DO_STOP="false";
OPTS=rSkh

if [[ "$#" -eq 0 ]]; then
    echo "$USAGE"
    exit 0
fi

# parse options
PARSED_OPTS=$(getopt -o "$OPTS" -n "$0" -- "$@")
if [ $? -ne 0 ]; then
    echo "Error parsing options."
    exit 1
fi
eval set -- "$PARSED_OPTS"

while true; do
    case "$1" in
        -r) DO_CLEANUP="true"; shift;;
        -S) DO_LAUNCH="true"; shift;;
        -k) DO_STOP="true"; shift;;
        -h) echo "$USAGE"; exit 0;;
        --) shift; break;;
        *) echo "Internal error: $1"; exit 1;;
    esac
done

if [[ "$DO_LAUNCH" == "true" && "$DO_STOP" == "true" ]]; then
    echo "$USAGE"
    exit 1
fi

if [[ "$DO_CLEANUP" == "true" ]]; then
    echo "Cleaning crawler..."
    rm -rf ${LOG_FILE} && echo "Removed $LOG_FILE"
    rm -rf ${FRONTIER} && echo "Removed $FRONTIER"
    echo "Cleanup complete"
fi

if [[ "$DO_LAUNCH" == "true" ]]; then
    echo "Starting crawler in detached session $SESSION_NAME..."
    if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux new-session -d -s "$SESSION_NAME"
        echo "Created new session "$SESSION_NAME""
    fi
    tmux send-keys -t $SESSION_NAME "$ACTIVATE_VENV; $LAUNCH_CMD" Enter;
    echo "Crawler started. Detach with Ctrl-b, d"
fi

if [[ "$DO_STOP" == "true" ]]; then
    echo "Stopping crawler in detached session "$SESSION_NAME"..."
    PIDS=$(ps aux | grep "$USER" | grep -v grep | grep "$LAUNCH_CMD" | awk '{print $2}' | tr '\n' ' ')
    if [ -z "$PIDS" ]; then
        echo "No running crawler processes found."
    else
        echo "Found running crawler PIDS: $PIDS"
        for PID in $PIDS; do
            echo "Killing $PID..."
            kill -9 "$PID" 2>/dev/null && echo "PID $PID terminated." || echo "Failed to kill PID $PID."
        done
    fi
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux kill-session -t "$SESSION_NAME"
        echo "tmux session $SESSION_NAME closed."
    fi
fi