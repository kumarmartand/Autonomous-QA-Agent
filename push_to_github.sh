#!/bin/bash
# Script to push project to GitHub

echo "🚀 Pushing QA Agent project to GitHub"
echo ""
echo "⚠️  IMPORTANT: Create a new repository on GitHub first!"
echo "   1. Go to https://github.com/new"
echo "   2. Create a new repository (don't initialize with README)"
echo "   3. Copy the repository URL"
echo ""
read -p "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Repository URL is required. Exiting."
    exit 1
fi

echo ""
echo "Adding remote and pushing..."
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Next steps:"
    echo "1. Deploy backend: See DEPLOYMENT.md"
    echo "2. Deploy frontend on Streamlit Cloud:"
    echo "   - Go to https://share.streamlit.io"
    echo "   - Connect your GitHub repo"
    echo "   - Set main file: ui/streamlit_app.py"
    echo "   - Add API_BASE_URL environment variable"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   - Repository URL is correct"
    echo "   - You have push access"
    echo "   - GitHub credentials are configured"
fi

