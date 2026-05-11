#!/bin/bash

# chmod a+x scripts/run_server.sh

echo "Booting server..."
uvicorn scripts.main:app --reload --port 8000