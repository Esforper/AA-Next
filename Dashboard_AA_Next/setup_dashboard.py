# setup_dashboard.py - Dashboard kurulum scripti
#!/usr/bin/env python3

import os
from pathlib import Path

def setup_dashboard():
    """Dashboard için gerekli dosya ve klasörleri oluştur"""
    
    print("🎯 AA News API Dashboard Setup")
    print("=" * 40)
    
    # Ana dashboard dizini
    dashboard_dir = Path("dashboard")
    dashboard_dir.mkdir(exist_ok=True)
    
    # Templates dizini
    templates_dir = dashboard_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Template dosyalarını oluştur
    templates = {
        "base.html": """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AA News API Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #2c3e50; }
        .sidebar .nav-link { color: #ecf0f1; }
        .sidebar .nav-link:hover { background: #34495e; color: white; }
        .sidebar .nav-link.active { background: #3498db; color: white; }
        .content-wrapper { min-height: 100vh; }
        .json-container { background: #f8f9fa; border-radius: 5px; padding: 15px; }
        pre { font-size: 12px; }
        .card-hover:hover { transform: translateY(-2px); transition: all 0.3s; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 d-none d-md-block sidebar">
                <div class="sidebar-sticky pt-3">
                    <h5 class="text-center text-white mb-4">
                        <i class="fas fa-newspaper"></i> AA News API
                    </h5>
                    
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/">
                                <i class="fas fa-tachometer-alt"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/news">
                                <i class="fas fa-newspaper"></i> News Manager
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/tts">
                                <i class="fas fa-volume-up"></i> TTS Manager
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/reels">
                                <i class="fas fa-film"></i> Reels Manager
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/api-tester">
                                <i class="fas fa-tools"></i> API Tester
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/monitoring">
                                <i class="fas fa-chart-line"></i> Monitoring
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/data-browser">
                                <i class="fas fa-database"></i> Data Browser
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-10 ml-sm-auto content-wrapper">
                <div class="container-fluid py-4">
                    {% block content %}{% endblock %}
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>""",
        
        "dashboard.html": """{% extends "base.html" %}

{% block title %}Dashboard - AA News API{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h1><i class="fas fa-tachometer-alt"></i> API Dashboard</h1>
        <p class="text-muted">AA News Universal API Control Panel</p>
    </div>
</div>

<!-- Status Cards -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card card-hover">
            <div class="card-body text-center">
                <h5 class="card-title">{{ stats.api_status }}</h5>
                <p class="card-text">API Status</p>
                <small class="text-muted">Last check: {{ stats.last_check }}</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-hover">
            <div class="card-body text-center">
                <h5 class="card-title">{{ stats.total_endpoints }}</h5>
                <p class="card-text">Total Endpoints</p>
                <small class="text-muted">Available APIs</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-hover">
            <div class="card-body text-center">
                <h5 class="card-title">{{ stats.audio_files }}</h5>
                <p class="card-text">Audio Files</p>
                <small class="text-muted">Generated TTS</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-hover">
            <div class="card-body text-center">
                <h5 class="card-title">
                    {% if system_status.success %}🟢{% else %}🔴{% endif %}
                </h5>
                <p class="card-text">System Health</p>
                <small class="text-muted">All services</small>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions -->
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-bolt"></i> Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="/news" class="btn btn-primary me-2 mb-2">
                    <i class="fas fa-newspaper"></i> Fetch News
                </a>
                <a href="/tts" class="btn btn-success me-2 mb-2">
                    <i class="fas fa-microphone"></i> Generate TTS
                </a>
                <a href="/reels" class="btn btn-info me-2 mb-2">
                    <i class="fas fa-film"></i> Manage Reels
                </a>
                <a href="/api-tester" class="btn btn-warning me-2 mb-2">
                    <i class="fas fa-tools"></i> Test APIs
                </a>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-info-circle"></i> System Information</h5>
            </div>
            <div class="card-body">
                {% if system_status.success %}
                    <div class="json-container">
                        <pre>{{ system_status.data | tojson(indent=2) }}</pre>
                    </div>
                {% else %}
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        System status unavailable: {{ system_status.error }}
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    }
    
    # Template dosyalarını yaz
    for filename, content in templates.items():
        template_file = templates_dir / filename
        template_file.write_text(content, encoding='utf-8')
        print(f"✅ Created: {template_file}")
    
    # Main dashboard.py dosyası
    dashboard_py = dashboard_dir / "dashboard.py"
    dashboard_py.write_text('''#!/usr/bin/env python3
# ================================
# dashboard.py - AA News API Dashboard
# ================================

from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.template_folder = 'templates'

# API Base URL
API_BASE = "http://localhost:8000"

def api_call(endpoint, method="GET", data=None, params=None):
    """API çağrısı yapma helper"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
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

@app.route('/')
def dashboard():
    """Ana dashboard"""
    
    # System health check
    health = api_call("/health")
    system_status = api_call("/api/system/health")
    
    # Quick stats
    stats = {
        "api_status": "🟢 Online" if health["success"] else "🔴 Offline",
        "total_endpoints": 25,
        "audio_files": 0,
        "last_check": datetime.now().strftime("%H:%M:%S")
    }
    
    # Audio files count
    try:
        files_result = api_call("/api/tts/files")
        if files_result["success"] and files_result["data"].get("success"):
            stats["audio_files"] = len(files_result["data"]["files"])
    except:
        pass
    
    return render_template('dashboard.html', 
                         health=health, 
                         system_status=system_status,
                         stats=stats)

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

@app.route('/tts')
def tts_manager():
    """TTS yönetimi"""
    
    # Available voices
    voices_result = api_call("/api/tts/voices")
    voices = voices_result["data"].get("voices", {}) if voices_result["success"] else {}
    
    # Audio files
    files_result = api_call("/api/tts/files")
    audio_files = files_result["data"].get("files", []) if files_result["success"] else []
    
    return render_template('tts.html',
                         voices=voices,
                         audio_files=audio_files)

@app.route('/reels')
def reels_manager():
    """Reels yönetimi"""
    
    # Mockup data
    mockup_result = api_call("/api/reels/mockup/scraped-news", params={"count": 5})
    trending_result = api_call("/api/reels/trending")
    
    return render_template('reels.html',
                         mockup_result=mockup_result,
                         trending_result=trending_result)

@app.route('/api-tester')
def api_tester():
    """API test aracı"""
    
    endpoints = [
        {"name": "Health Check", "method": "GET", "url": "/health"},
        {"name": "Latest News", "method": "GET", "url": "/api/news/latest?count=5"},
        {"name": "TTS Voices", "method": "GET", "url": "/api/tts/voices"},
        {"name": "System Status", "method": "GET", "url": "/api/system/status"},
    ]
    
    return render_template('api_tester.html', endpoints=endpoints)

@app.route('/api-test', methods=['POST'])
def test_api():
    """API test et"""
    endpoint = request.form.get('endpoint')
    method = request.form.get('method', 'GET')
    
    result = api_call(endpoint, method=method)
    return jsonify(result)

if __name__ == '__main__':
    print("🎯 AA News API Dashboard Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("💡 Make sure your API is running on http://localhost:8000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
''', encoding='utf-8')
    
    print(f"✅ Created: {dashboard_py}")
    
    # requirements.txt for dashboard
    requirements_txt = dashboard_dir / "requirements.txt"
    requirements_txt.write_text('''Flask==2.3.3
requests==2.31.0
''', encoding='utf-8')
    
    print(f"✅ Created: {requirements_txt}")
    
    # Çalıştırma scripti
    run_script = dashboard_dir / "run_dashboard.py"
    run_script.write_text('''#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 Starting AA News API Dashboard")
    print("=" * 40)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        print("✅ API is running on http://localhost:8000")
    except:
        print("⚠️  API is not running on http://localhost:8000")
        print("   Please start your API first:")
        print("   cd .. && python main.py api")
        print()
    
    # Install requirements if needed
    try:
        import flask
        import requests
    except ImportError:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start dashboard
    print("🎯 Starting dashboard on http://localhost:5000")
    os.system("python dashboard.py")

if __name__ == "__main__":
    main()
''', encoding='utf-8')
    
    print(f"✅ Created: {run_script}")
    
    # Simple template dosyaları (minimal)
    simple_templates = {
        "news.html": '''{% extends "base.html" %}
{% block content %}
<h1>News Manager</h1>
<p>News management interface will be here</p>
{% endblock %}''',
        
        "tts.html": '''{% extends "base.html" %}
{% block content %}
<h1>TTS Manager</h1>
<p>TTS management interface will be here</p>
{% endblock %}''',
        
        "reels.html": '''{% extends "base.html" %}
{% block content %}
<h1>Reels Manager</h1>
<p>Reels management interface will be here</p>
{% endblock %}''',
        
        "api_tester.html": '''{% extends "base.html" %}
{% block content %}
<h1>API Tester</h1>
<div class="row">
    <div class="col-md-6">
        <h5>Quick Tests</h5>
        {% for endpoint in endpoints %}
        <button class="btn btn-outline-primary btn-sm me-2 mb-2" 
                onclick="testEndpoint('{{ endpoint.url }}', '{{ endpoint.method }}')">
            {{ endpoint.name }}
        </button>
        {% endfor %}
    </div>
    <div class="col-md-6">
        <h5>Manual Test</h5>
        <form onsubmit="return testManual(event)">
            <input type="text" class="form-control mb-2" id="manual-endpoint" placeholder="/api/news/latest" value="/health">
            <button type="submit" class="btn btn-primary">Test</button>
        </form>
    </div>
</div>
<div class="mt-4">
    <h5>Results</h5>
    <div id="test-results" class="border p-3" style="min-height: 200px; background: #f8f9fa;">
        Test results will appear here
    </div>
</div>

<script>
function testEndpoint(url, method) {
    fetch('/api-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ endpoint: url, method: method })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('test-results').innerHTML = 
            '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
    })
    .catch(err => {
        document.getElementById('test-results').innerHTML = 
            '<div class="alert alert-danger">Error: ' + err.message + '</div>';
    });
}

function testManual(event) {
    event.preventDefault();
    const endpoint = document.getElementById('manual-endpoint').value;
    testEndpoint(endpoint, 'GET');
    return false;
}
</script>
{% endblock %}'''
    }
    
    for filename, content in simple_templates.items():
        template_file = templates_dir / filename
        template_file.write_text(content, encoding='utf-8')
        print(f"✅ Created: {template_file}")
    
    print("\n🎉 Dashboard setup completed!")
    print("\n📋 Next steps:")
    print("1. cd dashboard")
    print("2. python run_dashboard.py")
    print("\n📚 Dashboard features:")
    print("- 📊 Real-time API monitoring")
    print("- 📰 News management interface")
    print("- 🎵 TTS file browser") 
    print("- 🎬 Reels generator")
    print("- 🔧 API testing tool")
    print("\n💡 Make sure your API is running on http://localhost:8000 first!")

if __name__ == "__main__":
    setup_dashboard()