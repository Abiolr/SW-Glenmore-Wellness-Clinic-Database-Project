# 🔧 Troubleshooting Guide

## Error: "Connection refused to localhost:27017"

This error means the application can't find your MongoDB Atlas connection string.

### Quick Fix (3 Steps)

#### Step 1: Create the .env file

In your project directory (`backend_v2`), create a file named `.env`:

```bash
# In your terminal, run:
cd /workspaces/SW-Glenmore-Wellness-Clinic-Database-Project/backend_v2
nano .env
```

#### Step 2: Add your MongoDB Atlas URL

Paste this into the `.env` file (replace with YOUR actual MongoDB Atlas URL):

```env
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=wellness_clinic
```

**How to get your MongoDB Atlas URL:**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your actual database password

**Example:**
```env
MONGODB_URL=mongodb+srv://admin:MySecurePass123@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=wellness_clinic
```

#### Step 3: Save and restart

1. Save the file (Ctrl+O, Enter, Ctrl+X in nano)
2. Restart your server:
```bash
uvicorn main:app --reload
```

### Verify It's Working

You should see:
```
Successfully connected to MongoDB database: wellness_clinic
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Then visit: http://127.0.0.1:8000/health

## Alternative: Set Environment Variables Directly

If you don't want to create a `.env` file, you can set the environment variables directly:

```bash
export MONGODB_URL="mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority"
export MONGODB_DB_NAME="wellness_clinic"
uvicorn main:app --reload
```

## Common Issues

### Issue 1: Still getting localhost:27017 error
**Solution:** Make sure the `.env` file is in the same directory as `main.py`

Check with:
```bash
ls -la .env
```

### Issue 2: "Authentication failed"
**Solution:** Check your MongoDB Atlas username and password are correct in the connection string

### Issue 3: "Network timeout"
**Solutions:**
1. Check your MongoDB Atlas IP whitelist includes your current IP
2. Or allow access from anywhere (0.0.0.0/0) for development

**To whitelist your IP:**
1. Go to MongoDB Atlas
2. Network Access → Add IP Address
3. Either add your current IP or use 0.0.0.0/0 for development

### Issue 4: .env file not being read
**Solution:** Make sure `python-dotenv` is installed:
```bash
pip install python-dotenv
```

## Quick Checklist

- [ ] `.env` file exists in the same directory as `main.py`
- [ ] `MONGODB_URL` is set with your actual Atlas URL
- [ ] Password in URL doesn't contain special characters (or is URL-encoded)
- [ ] MongoDB Atlas cluster is running
- [ ] IP address is whitelisted in MongoDB Atlas
- [ ] `python-dotenv` is installed

## Test Your Connection

Run this Python script to test your MongoDB connection:

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
print(f"Attempting to connect to: {mongodb_url[:20]}...")

try:
    client = MongoClient(mongodb_url)
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    print(f"Database: {os.getenv('MONGODB_DB_NAME')}")
except Exception as e:
    print(f"Connection failed: {e}")
```

Save as `test_connection.py` and run:
```bash
python test_connection.py
```

## Still Having Issues?

1. Double-check your `.env` file format (no quotes around values needed)
2. Make sure there are no extra spaces
3. Verify your MongoDB Atlas cluster is active
4. Try connecting with MongoDB Compass using the same connection string

## Example Working .env File

```env
MONGODB_URL=mongodb+srv://clinicadmin:SecurePassword123@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=wellness_clinic
```

**Important:** 
- No quotes around values
- No spaces around the `=` sign
- Replace with your actual credentials
- Never commit this file to Git (it's in .gitignore)
