# MongoDB Atlas Setup Guide

## Connection Issue Resolution

If you're experiencing connection timeouts when running `test_db_connection.py`, follow these steps:

### 1. Whitelist Your IP Address

MongoDB Atlas requires IP whitelisting for security:

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Log in with your credentials
3. Select your cluster (cluster0)
4. Click on "Network Access" in the left sidebar
5. Click "Add IP Address"
6. Either:
   - Click "Add Current IP Address" to whitelist your current IP
   - Click "Allow Access from Anywhere" (0.0.0.0/0) for development (NOT recommended for production)
7. Click "Confirm"

Wait 1-2 minutes for the changes to propagate.

### 2. Verify Database User Credentials

1. In MongoDB Atlas, click on "Database Access" in the left sidebar
2. Verify that the user `mdjunaidadil` exists
3. If the password is incorrect, click "Edit" and update it
4. Update the `.env` file with the correct password

### 3. Test the Connection

After whitelisting your IP, run the test script:

```bash
cd filter/filter/backend
python test_db_connection.py
```

You should see:
```
✓ MongoDB connected successfully
✓ Database indexes created successfully
✓ Database health check passed
✓ All database tests passed successfully!
```

### 4. Connection String Format

The connection string in `.env` should follow this format:

```
MONGODB_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/YOUR_DATABASE?retryWrites=true&w=majority
```

**Important**: If your password contains special characters, you need to URL-encode them:
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `?` → `%3F`
- `#` → `%23`
- `[` → `%5B`
- `]` → `%5D`
- `%` → `%25`

### 5. Firewall/Network Issues

If you're behind a corporate firewall or VPN:
- MongoDB Atlas uses port 27017
- Ensure your firewall allows outbound connections to `*.mongodb.net` on port 27017
- Try disabling VPN temporarily to test

### 6. Verify Cluster Status

1. In MongoDB Atlas, go to your cluster
2. Ensure the cluster status shows "Active" (green)
3. If it shows "Paused", click "Resume" to activate it

## Testing Without MongoDB (Optional)

If you want to proceed with development without MongoDB connection:
- You can skip the database tests for now
- The FastAPI application will fail to start without a valid MongoDB connection
- Consider using a local MongoDB instance for development:
  ```bash
  # Install MongoDB locally or use Docker
  docker run -d -p 27017:27017 --name mongodb mongo:latest
  
  # Update .env to use local MongoDB
  MONGODB_URI=mongodb://localhost:27017/resume_filter
  ```

## Next Steps

Once the connection is successful:
1. The database service is ready to use
2. Indexes will be created automatically on startup
3. You can proceed with implementing the API endpoints
