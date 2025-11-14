# ✅ Your .env File Configuration

Use this **exact** configuration for your project:

```dotenv
MONGODB_URI=mongodb+srv://habuq028_db_user:n3HdeFLHS5iE7dAb@glenmorewellnesscluster.zfgmoag.mongodb.net/?appName=GlenmoreWellnessCluster
MONGODB_DB_NAME=GlenmoreWellnessDB
```

## Quick Setup

1. **Copy the file** to your project:
   ```bash
   cd /workspaces/SW-Glenmore-Wellness-Clinic-Database-Project/backend_v2
   ```

2. **Create .env** file:
   ```bash
   nano .env
   ```

3. **Paste the content** above, then save (Ctrl+O, Enter, Ctrl+X)

4. **Restart the server**:
   ```bash
   uvicorn main:app --reload
   ```

## ✅ What You Should See

```
Successfully connected to MongoDB database: GlenmoreWellnessDB
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Then visit: **http://127.0.0.1:8000/docs** to see your API!

## 🔍 Testing the Connection

Once running, test these endpoints:

1. **Health Check**: http://127.0.0.1:8000/health
2. **API Docs**: http://127.0.0.1:8000/docs
3. **Get Patients**: http://127.0.0.1:8000/patients

## 📝 Note

The code now supports **both**:
- `MONGODB_URL` (standard naming)
- `MONGODB_URI` (your naming)

So your configuration will work perfectly!

## ⚠️ Important Security Notes

1. **Never commit .env to Git** - it's already in .gitignore
2. Your database credentials are:
   - Username: `habuq028_db_user`
   - Password: `n3HdeFLHS5iE7dAb`
   - Cluster: `glenmorewellnesscluster.zfgmoag.mongodb.net`
   - Database: `GlenmoreWellnessDB`

3. **Make sure your IP is whitelisted** in MongoDB Atlas:
   - Go to MongoDB Atlas → Network Access
   - Add your current IP or use 0.0.0.0/0 for development

## 🚀 You're Ready!

Your backend is now properly configured to connect to your MongoDB Atlas cluster with all 23 collections ready to use!
