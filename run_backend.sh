#!/bin/bash
# Script to run the FastAPI backend

echo "Starting FastAPI backend..."
echo "API will be available at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

