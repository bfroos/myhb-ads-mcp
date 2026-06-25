#!/usr/bin/env python3
"""
GitHub Webhook Handler für Auto-Deploy
Läuft auf Hetzner, wartet auf GitHub Push-Events
"""
import os
import json
import subprocess
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook Secret (setzen in GitHub Repo Settings → Webhooks)
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "your-secret-here")
REPO_PATH = "/opt/google-ads-mcp"
SERVICE_NAME = "google-ads-mcp"

def verify_signature(payload_body, signature):
    """Verify GitHub webhook signature"""
    if not signature:
        return False
    hash_obj = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_sig = "sha256=" + hash_obj.hexdigest()
    return hmac.compare_digest(expected_sig, signature)

@app.route('/', methods=['POST'])
@app.route('/deploy', methods=['POST'])
def deploy():
    """Handle GitHub Push webhook"""
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    # Verify signature
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 403
    
    payload = request.get_json()
    
    # Only deploy on main branch
    if payload.get('ref') != 'refs/heads/main':
        return jsonify({"status": "Skipped (not main branch)"}), 200
    
    try:
        # Change to repo directory
        os.chdir(REPO_PATH)
        
        # Pull latest code
        subprocess.run(['git', 'fetch', 'origin', 'main'],
                      check=True, capture_output=True)
        subprocess.run(['git', 'reset', '--hard', 'origin/main'],
                      check=True, capture_output=True)
        
        # Verify Python syntax
        subprocess.run(['python3', '-m', 'py_compile', 'server.py'],
                      check=True, capture_output=True)
        
        # Restart service
        subprocess.run(['sudo', 'systemctl', 'restart', SERVICE_NAME],
                      check=True, capture_output=True)
        
        # Give service time to start
        import time
        time.sleep(2)
        
        # Check service status
        result = subprocess.run(['systemctl', 'is-active', SERVICE_NAME],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                "status": "✅ Deploy successful",
                "commit": payload.get('after', 'unknown')[:7],
                "service": "running"
            }), 200
        else:
            return jsonify({
                "status": "⚠️ Deploy completed but service may have issues",
                "service_status": result.stdout
            }), 200
            
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": f"Deploy failed: {e.stderr.decode() if e.stderr else str(e)}",
            "status": "❌"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "✅ Webhook handler running"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=False)
