from flask import Flask, request, redirect, render_template_string, jsonify
import json
import string
import random
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = os.getenv('DATA_FILE', '/data/urls.json')

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>qlo.in - URL Shortener</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 { color: #667eea; margin-bottom: 10px; font-size: 2.5em; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"], input[type="url"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:active { transform: translateY(0); }
        .result {
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: #f0f4ff;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .result.show { display: block; }
        .short-url {
            font-size: 1.2em;
            color: #667eea;
            font-weight: 600;
            word-break: break-all;
            margin: 10px 0;
        }
        .copy-btn {
            padding: 8px 16px;
            font-size: 14px;
            margin-top: 10px;
        }
        .error {
            color: #dc3545;
            margin-top: 10px;
            display: none;
        }
        .stats {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            color: #666;
        }
        .stat-value {
            font-weight: 600;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>qlo.in</h1>
        <p class="subtitle">Shorten your URLs instantly</p>
        
        <div class="input-group">
            <input type="url" id="urlInput" placeholder="Enter your long URL here..." required>
            <button onclick="shortenUrl()">Shorten</button>
        </div>
        
        <div class="input-group">
            <input type="text" id="customCode" placeholder="Custom short code (optional)">
        </div>
        
        <div class="result" id="result">
            <p>Your shortened URL:</p>
            <div class="short-url" id="shortUrl"></div>
            <button class="copy-btn" onclick="copyUrl()">Copy to Clipboard</button>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="stats">
            <h3 style="margin-bottom: 15px; color: #333;">Statistics</h3>
            <div class="stat-item">
                <span>Total URLs:</span>
                <span class="stat-value" id="totalUrls">{{ total_urls }}</span>
            </div>
            <div class="stat-item">
                <span>Total Clicks:</span>
                <span class="stat-value" id="totalClicks">{{ total_clicks }}</span>
            </div>
        </div>
    </div>

    <script>
        async function shortenUrl() {
            const url = document.getElementById('urlInput').value;
            const customCode = document.getElementById('customCode').value;
            const resultDiv = document.getElementById('result');
            const errorDiv = document.getElementById('error');
            
            if (!url) {
                showError('Please enter a URL');
                return;
            }
            
            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, custom_code: customCode })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('shortUrl').textContent = data.short_url;
                    resultDiv.classList.add('show');
                    errorDiv.style.display = 'none';
                    updateStats();
                } else {
                    showError(data.error || 'Failed to shorten URL');
                }
            } catch (error) {
                showError('Network error. Please try again.');
            }
        }
        
        function copyUrl() {
            const shortUrl = document.getElementById('shortUrl').textContent;
            navigator.clipboard.writeText(shortUrl).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            });
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            document.getElementById('result').classList.remove('show');
        }
        
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('totalUrls').textContent = data.total_urls;
                document.getElementById('totalClicks').textContent = data.total_clicks;
            } catch (error) {
                console.error('Failed to update stats');
            }
        }
        
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') shortenUrl();
        });
    </script>
</body>
</html>
"""

def init_data_file():
    """Initialize the JSON data file if it doesn't exist"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

def read_data():
    """Read all URL data from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_data(data):
    """Write URL data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_short_code(length=6):
    """Generate a random short code"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/')
def index():
    """Home page with URL shortener interface"""
    data = read_data()
    total_urls = len(data)
    total_clicks = sum(url_data.get('clicks', 0) for url_data in data.values())
    return render_template_string(HTML_TEMPLATE, total_urls=total_urls, total_clicks=total_clicks)

@app.route('/api/shorten', methods=['POST'])
def shorten():
    """API endpoint to create a shortened URL"""
    request_data = request.json
    original_url = request_data.get('url')
    custom_code = request_data.get('custom_code', '').strip()
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add https:// if not present
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
    # Load existing data
    data = read_data()
    
    # Handle custom code
    if custom_code:
        if len(custom_code) < 3 or len(custom_code) > 20:
            return jsonify({'error': 'Custom code must be 3-20 characters'}), 400
        
        if not custom_code.replace('_', '').replace('-', '').isalnum():
            return jsonify({'error': 'Custom code can only contain letters, numbers, hyphens, and underscores'}), 400
        
        if custom_code in data:
            return jsonify({'error': 'Custom code already taken'}), 400
        
        short_code = custom_code
    else:
        # Generate random code
        while True:
            short_code = generate_short_code()
            if short_code not in data:
                break
    
    # Save the URL data
    data[short_code] = {
        'url': original_url,
        'clicks': 0,
        'created_at': datetime.now().isoformat()
    }
    write_data(data)
    
    short_url = f"{request.host_url}{short_code}"
    return jsonify({'short_url': short_url, 'short_code': short_code})

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect short code to original URL"""
    data = read_data()
    
    if short_code in data:
        # Increment click counter
        data[short_code]['clicks'] = data[short_code].get('clicks', 0) + 1
        write_data(data)
        
        return redirect(data[short_code]['url'])
    
    return "URL not found", 404

@app.route('/api/stats')
def stats():
    """Get statistics about URLs"""
    data = read_data()
    total_urls = len(data)
    total_clicks = sum(url_data.get('clicks', 0) for url_data in data.values())
    return jsonify({'total_urls': total_urls, 'total_clicks': total_clicks})

@app.route('/api/list')
def list_urls():
    """List all URLs (for personal use)"""
    data = read_data()
    urls = []
    for code, info in data.items():
        urls.append({
            'short_code': code,
            'url': info['url'],
            'clicks': info.get('clicks', 0),
            'created_at': info.get('created_at', 'Unknown')
        })
    return jsonify(urls)

if __name__ == '__main__':
    init_data_file()
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
