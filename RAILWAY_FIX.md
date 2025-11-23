# Railway Deployment Fix - "uvicorn: command not found"

## Problem
Railway can't find the `uvicorn` command because:
1. Dependencies might not be installed correctly
2. Using `uvicorn` directly instead of `python -m uvicorn`

## Solution Applied

### Files Updated:
1. **Procfile** - Changed to use `python -m uvicorn` instead of `uvicorn`
2. **railway.json** - Added Railway-specific configuration
3. **nixpacks.toml** - Added Nixpacks configuration for Railway

### Railway Configuration:

**Option 1: Use Procfile (Recommended)**
- Railway auto-detects `Procfile`
- Already configured with: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Option 2: Manual Settings**
If Railway doesn't auto-detect, set manually:
- **Build Command**: `pip install -r requirements-backend.txt`
- **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Steps to Fix on Railway:

1. **Go to Railway Dashboard**
2. **Select your service**
3. **Go to Settings tab**
4. **Check/Update**:
   - **Build Command**: `pip install -r requirements-backend.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Redeploy** (or push new commit to trigger redeploy)

## Why `python -m uvicorn`?

- `uvicorn` command requires it to be in PATH
- `python -m uvicorn` uses Python's module system
- More reliable across different environments
- Works even if uvicorn isn't in system PATH

## Verification:

After redeploy, check logs for:
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:PORT"
- ❌ No more "uvicorn: command not found" errors

## Alternative: If Still Not Working

If the issue persists, try:

1. **Check Python version**:
   - Railway should use Python 3.8+
   - Can set in `runtime.txt` (already set to python-3.11)

2. **Check build logs**:
   - Verify `pip install -r requirements-backend.txt` completes successfully
   - Look for any installation errors

3. **Use virtual environment** (if needed):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-backend.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Manual start command**:
   ```
   sh -c "pip install -r requirements-backend.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
   ```

