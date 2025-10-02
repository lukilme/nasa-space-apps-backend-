#!/bin/sh
set -e

ollama serve &
PID=$!

sleep 5

ollama pull llama3 || true

wait $PID
