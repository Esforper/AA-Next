# ================================
# dashboard.py - AA News API Dashboard
# ================================

"""
Flask tabanlı API Dashboard
- API test aracı
- Veri görüntüleyici  
- Feed manager
- Real-time monitoring
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)

# API Base URL
API_BASE = "http://localhost:8000"

# ============ UTILITY FUNCTIONS ============

def api_call(endpoint, method="GET", data=None, params=None):
    """API çağrısı yapma helper"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url if 'url' in locals() else endpoint
        }

def get_audio_files():
    """Audio dosyalarını listele"""
    try:
        result = api_call("/api/tts/files")
        if result["success"] and result["data"].get("success"):
            return result["data"]["files"]
        return []
    except:
        return []

# ============ MAIN ROUTES ============

@app.route('/')
def dashboard():
    """Ana dashboard"""
    
    # System health check
    health = api_call("/health")
    system_status = api_call("/api/system/health")
    
    # Quick stats
    stats = {
        "api_status": "🟢 Online" if health["success"] else "🔴 Offline",
        "total_endpoints": 25,  # Approximate
        "audio_files": len(get_audio_files()),
        "last_check": datetime.now().strftime("%H:%M:%S")
    }
    
    return render_template('dashboard.html', 
                         health=health, 
                         system_status=system_status,
                         stats=stats)

# ============ NEWS ROUTES ============

@app.route('/news')
def news_manager():
    """Haber yönetimi"""
    
    # Categories
    categories_result = api_call("/api/news/categories")
    categories = categories_result["data"].get("categories", []) if categories_result["success"] else []
    
    # Latest news (default)
    news_result = api_call("/api/news/latest", params={"count": 10})
    
    return render_template('news.html', 
                         categories=categories,
                         news_result=news_result)

@app.route('/news/fetch', methods=['POST'])
def fetch_news():
    """Haber çekme"""
    count = request.form.get('count', 10)
    category = request.form.get('category', 'guncel')
    scraping = 'scraping' in request.form
    
    result = api_call("/api/news/latest", params={
        "count": count,
        "category": category,
        "enable_scraping": scraping
    })
    
    return jsonify(result)

@app.route('/news/search', methods=['POST'])
def search_news():
    """Haber arama"""
    query = request.form.get('query')
    category = request.form.get('category')
    
    params = {"q": query}
    if category:
        params["category"] = category
    
    result = api_call("/api/news/search", params=params)
    return jsonify(result)

# ============ TTS ROUTES ============

@app.route('/tts')
def tts_manager():
    """TTS yönetimi"""
    
    # Available voices
    voices_result = api_call("/api/tts/voices")
    voices = voices_result["data"].get("voices", {}) if voices_result["success"] else {}
    
    # Audio files
    files_result = api_call("/api/tts/files")
    audio_files = files_result["data"].get("files", []) if files_result["success"] else []
    
    # TTS stats
    stats_result = api_call("/api/tts/stats")
    
    return render_template('tts.html',
                         voices=voices,
                         audio_files=audio_files,
                         stats_result=stats_result)

@app.route('/tts/convert', methods=['POST'])
def convert_tts():
    """TTS dönüştürme"""
    text = request.form.get('text')
    voice = request.form.get('voice', 'alloy')
    model = request.form.get('model', 'tts-1')
    
    data = {
        "text": text,
        "voice": voice,
        "model": model
    }
    
    result = api_call("/api/tts/convert", method="POST", data=data)
    return jsonify(result)

@app.route('/tts/convert-url', methods=['POST'])
def convert_url_tts():
    """URL'den TTS"""
    url = request.form.get('url')
    voice = request.form.get('voice', 'alloy')
    
    data = {
        "url": url,
        "voice": voice
    }
    
    result = api_call("/api/tts/convert-article", method="POST", data=data)
    return jsonify(result)

# ============ REELS ROUTES ============

@app.route('/reels')
def reels_manager():
    """Reels yönetimi"""
    
    # Mockup scraped news
    mockup_result = api_call("/api/reels/mockup/scraped-news", params={"count": 5})
    
    # Trending reels
    trending_result = api_call("/api/reels/trending", params={"limit": 10})
    
    # Latest published
    latest_result = api_call("/api/reels/latest-published")
    
    return render_template('reels.html',
                         mockup_result=mockup_result,
                         trending_result=trending_result,
                         latest_result=latest_result)

@app.route('/reels/generate', methods=['POST'])
def generate_reels():
    """Reels generate et"""
    count = request.form.get('count', 3)
    voice = request.form.get('voice', 'alloy')
    category = request.form.get('category')
    
    params = {
        "count": count,
        "voice": voice
    }
    if category:
        params["category"] = category
    
    result = api_call("/api/reels/mockup/generate-reels", params=params)
    return jsonify(result)

@app.route('/reels/user/<user_id>')
def user_reels(user_id):
    """Kullanıcı reels bilgileri"""
    
    # User stats
    stats_result = api_call(f"/api/reels/user/{user_id}/stats")
    
    # Daily progress
    progress_result = api_call(f"/api/reels/user/{user_id}/daily-progress")
    
    # Watched reels
    watched_result = api_call(f"/api/reels/user/{user_id}/watched", params={"limit": 20})
    
    return render_template('user_reels.html',
                         user_id=user_id,
                         stats_result=stats_result,
                         progress_result=progress_result,
                         watched_result=watched_result)

# ============ API TESTER ROUTES ============

@app.route('/api-tester')
def api_tester():
    """API test aracı"""
    
    # Common endpoints
    endpoints = [
        {"name": "Health Check", "method": "GET", "url": "/health"},
        {"name": "Latest News", "method": "GET", "url": "/api/news/latest?count=5"},
        {"name": "News Categories", "method": "GET", "url": "/api/news/categories"},
        {"name": "TTS Voices", "method": "GET", "url": "/api/tts/voices"},
        {"name": "TTS Files", "method": "GET", "url": "/api/tts/files"},
        {"name": "Trending Reels", "method": "GET", "url": "/api/reels/trending"},
        {"name": "System Status", "method": "GET", "url": "/api/system/status"},
    ]
    
    return render_template('api_tester.html', endpoints=endpoints)

@app.route('/api-test', methods=['POST'])
def test_api():
    """API test et"""
    endpoint = request.form.get('endpoint')
    method = request.form.get('method', 'GET')
    
    try:
        data = request.form.get('data')
        if data:
            data = json.loads(data)
    except:
        data = None
    
    result = api_call(endpoint, method=method, data=data)
    return jsonify(result)

# ============ MONITORING ROUTES ============

@app.route('/monitoring')
def monitoring():
    """System monitoring"""
    
    # System health
    system_result = api_call("/api/system/health")
    
    # System status
    status_result = api_call("/api/system/status")
    
    # Providers
    providers_result = api_call("/api/system/providers")
    
    # Stats
    stats_result = api_call("/api/system/stats")
    
    return render_template('monitoring.html',
                         system_result=system_result,
                         status_result=status_result,
                         providers_result=providers_result,
                         stats_result=stats_result)

# ============ DATA BROWSER ============

@app.route('/data-browser')
def data_browser():
    """Veri tarayıcısı"""
    
    # Audio files
    audio_files = get_audio_files()
    
    # Storage info
    storage_info = {
        "audio_count": len(audio_files),
        "total_size_mb": sum(f.get("size_mb", 0) for f in audio_files),
        "recent_files": audio_files[:10]
    }
    
    return render_template('data_browser.html',
                         storage_info=storage_info,
                         audio_files=audio_files)

# ============ TEMPLATES (Embedded) ============

@app.route('/templates/<template_name>')
def serve_template(template_name):
    """Template serving for development"""
    return render_template(template_name)

if __name__ == '__main__':
    # Template directory oluştur
    template_dir = Path(__file__).parent / 'templates'
    template_dir.mkdir(exist_ok=True)
    
    print("🎯 AA News API Dashboard Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 API Tester: http://localhost:5000/api-tester")
    print("📈 Monitoring: http://localhost:5000/monitoring")
    print("📁 Data Browser: http://localhost:5000/data-browser")
    print("\n💡 Make sure your API is running on http://localhost:8000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)