#!/bin/bash
# Script to run the Streamlit UI

echo "Starting Streamlit UI..."
echo "UI will be available at http://localhost:8501"
echo ""
streamlit run ui/streamlit_app.py --server.port 8501

