# qlo.in URL Shortener

A simple, fast URL shortener that you can deploy on Render.com using Docker.

## Features

- ✨ Clean, modern web interface
- 🔗 Generate random or custom short codes
- 📊 Real-time statistics (total URLs, total clicks)
- 💾 SQLite database for persistence
- 🐳 Docker-ready for easy deployment
- 📱 Responsive design

## Files Needed

Create these 4 files in your project directory:

1. **app.py** - The main Flask application
2. **Dockerfile** - Docker configuration
3. **requirements.txt** - Python dependencies
4. **urls.json** - Initial data file (can be empty: `{}`)

## Deploy to Render.com

### Step 1: Prepare Your Repository

1. Create a new GitHub repository
2. Add all four files:
   - `app.py` - Main application
   - `Dockerfile` - Docker config
   - `requirements.txt` - Dependencies
   - `urls.json` - Data template (can be empty `{}`)
3. Commit and push to GitHub

### Step 2: Deploy on Render

1. Go to [Render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `qlo-in-shortener` (or your choice)
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Instance Type**: Free (or paid for better performance)

5. Add a Disk for persistent storage:
   - Click "Add Disk"
   - **Name**: `data`
   - **Mount Path**: `/data`
   - **Size**: 1 GB (free tier)

6. Click "Create Web Service"

### Step 3: Configure Custom Domain (qlo.in)

1. After deployment, go to your service's "Settings"
2. Scroll to "Custom Domain"
3. Click "Add Custom Domain"
4. Enter: `qlo.in` and `www.qlo.in`
5. Render will provide DNS records
6. Go to your domain registrar (where you bought qlo.in)
7. Add the DNS records provided by Render:
   - **A Record**: Point `@` to Render's IP
   - **CNAME**: Point `www` to your Render URL

### DNS Configuration Example

At your domain registrar, add:

```
Type    Name    Value
A       @       216.24.57.1 (Render's IP)
CNAME   www     qlo-in-shortener.onrender.com
```

Wait 5-60 minutes for DNS propagation.

## Environment Variables (Optional)

You can set these in Render's dashboard under "Environment":

- `PORT` - Port number (default: 10000)
- `DB_PATH` - Database path (default: /data/urls.db)

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:10000`

## Using Docker Locally

```bash
# Build the image
docker build -t url-shortener .

# Run the container
docker run -p 10000:10000 -v $(pwd)/data:/data url-shortener
```

## File-Based Storage

This app uses a simple JSON file for storage:

- **Template file**: `urls.json` (included in repo)
- **Runtime file**: `/data/urls.json` (on Render disk)

When the app starts, it copies `urls.json` from your repo to `/data/urls.json` if it doesn't exist. This means:
- ✅ Your repo has a clean starting point
- ✅ Runtime data is saved to persistent disk
- ✅ Redeploying won't lose your URLs (they're on the disk)

### File Structure:

```json
{
  "abc123": {
    "url": "https://example.com/long-url",
    "clicks": 42,
    "created_at": "2025-10-02T10:30:00"
  },
  "mylink": {
    "url": "https://another-example.com",
    "clicks": 15,
    "created_at": "2025-10-02T11:00:00"
  }
}
```

### Advantages:
- ✅ Simple and lightweight
- ✅ Easy to backup (just copy the JSON file)
- ✅ Easy to edit manually if needed
- ✅ No database dependencies
- ✅ Perfect for personal use

### Viewing Your URLs

Access `/api/list` to see all your shortened URLs:
```
https://qlo.in/api/list
```

This returns JSON with all your URLs, clicks, and creation dates.

### POST /api/shorten
Create a short URL

**Request:**
```json
{
  "url": "https://example.com/very-long-url",
  "custom_code": "mycode" // optional
}
```

**Response:**
```json
{
  "short_url": "https://qlo.in/mycode",
  "short_code": "mycode"
}
```

### GET /{short_code}
Redirect to original URL

### GET /api/stats
Get statistics

**Response:**
```json
{
  "total_urls": 42,
  "total_clicks": 156
}
```

## Features Explained

### Custom Short Codes
- 3-20 characters allowed
- Letters, numbers, hyphens, underscores only
- Must be unique

### Automatic Short Codes
- 6-character random code
- Generated automatically if no custom code provided

### Click Tracking
- Every redirect increments the click counter
- View total clicks in statistics

## Troubleshooting

**Database not persisting:**
- Ensure disk is mounted at `/data` in Render
- Check disk is attached to your service

**Custom domain not working:**
- Wait for DNS propagation (up to 48 hours)
- Verify DNS records with `dig qlo.in`
- Check Render's custom domain status

**App not starting:**
- Check logs in Render dashboard
- Verify all files are present in repository
- Ensure Dockerfile is at root level

## Upgrading

To use production-ready server, update Dockerfile CMD to:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "app:app"]
```

## Support

For issues with:
- **Render deployment**: Check [Render Docs](https://render.com/docs)
- **DNS configuration**: Contact your domain registrar
- **Application bugs**: Check application logs

## License

Free to use and modify!