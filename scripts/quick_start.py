#!/usr/bin/env python3
"""
ToolLlama Quick Start
====================

Simplified startup script for testing the core functionality.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def start_backend():
    """Start the backend server"""
    print("🚀 Starting ToolLlama Backend...")

    backend_cmd = [
        sys.executable, "-c",
        """
import sys
sys.path.append('/home/scrapedat/projects/auction_intelligence')

# Simple FastAPI server for testing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def root():
    return {'message': 'ToolLlama Backend Running!', 'status': 'ok'}

@app.get('/health')
def health():
    return {
        'status': 'healthy',
        'services': {
            'backend': True,
            'context_manager': False,
            'browser_manager': False
        }
    }

@app.post('/api/tools/scrape_webpage')
def scrape_webpage(data: dict):
    return {
        'success': True,
        'result': {
            'url': data.get('url', ''),
            'method_used': 'test',
            'listings_found': 0,
            'data': []
        }
    }

# Browser Management Endpoints (Basic Implementation)
browser_sessions = {}

@app.post('/api/browser/create_session')
def create_browser_session():
    import uuid
    session_id = f"browser_{uuid.uuid4().hex[:8]}"
    browser_sessions[session_id] = {
        'session_id': session_id,
        'status': 'ready',
        'current_url': None,
        'ai_controlled': False,
        'created_at': '2024-01-01T00:00:00Z'
    }
    return {'success': True, 'session_id': session_id}

@app.get('/api/browser/sessions')
def get_browser_sessions():
    return {'sessions': list(browser_sessions.values())}

@app.post('/api/browser/{session_id}/navigate')
def navigate_browser_session(session_id: str, data: dict):
    if session_id not in browser_sessions:
        return {'success': False, 'error': 'Session not found'}

    url = data.get('url', '')
    browser_sessions[session_id]['current_url'] = url

    return {
        'success': True,
        'url': url,
        'title': f'Page: {url}',
        'screenshot': None  # No real screenshot in quick mode
    }

@app.post('/api/browser/{session_id}/action')
def execute_browser_action(session_id: str, data: dict):
    if session_id not in browser_sessions:
        return {'success': False, 'error': 'Session not found'}

    action = data.get('action', '')
    parameters = data.get('parameters', {})

    # Simulate browser actions
    if action == 'click':
        result = f"Clicked: {parameters.get('selector', 'element')}"
    elif action == 'type':
        result = f"Typed: {parameters.get('text', '')}"
    elif action == 'scroll':
        result = f"Scrolled: {parameters.get('direction', 'down')}"
    else:
        result = f"Executed: {action}"

    return {
        'success': True,
        'action': action,
        'result': result,
        'screenshot': None
    }

@app.get('/api/browser/{session_id}/screenshot')
def get_browser_screenshot(session_id: str):
    if session_id not in browser_sessions:
        return {'success': False, 'error': 'Session not found'}

    # Return a placeholder screenshot (base64 encoded simple image)
    import base64
    placeholder_image = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    screenshot_b64 = base64.b64encode(placeholder_image).decode('utf-8')

    return {'success': True, 'screenshot': screenshot_b64}

@app.post('/api/browser/{session_id}/enable_ai')
def enable_ai_control(session_id: str):
    if session_id not in browser_sessions:
        return {'success': False, 'error': 'Session not found'}

    browser_sessions[session_id]['ai_controlled'] = True
    return {'success': True, 'ai_controlled': True}

@app.post('/api/browser/{session_id}/disable_ai')
def disable_ai_control(session_id: str):
    if session_id not in browser_sessions:
        return {'success': False, 'error': 'Session not found'}

    browser_sessions[session_id]['ai_controlled'] = False
    return {'success': True, 'ai_controlled': False}

@app.get('/api/browser/{session_id}/info')
def get_browser_session_info(session_id: str):
    if session_id not in browser_sessions:
        return {'error': 'Session not found'}

    return browser_sessions[session_id]

@app.delete('/api/browser/{session_id}')
def close_browser_session(session_id: str):
    if session_id in browser_sessions:
        del browser_sessions[session_id]
        return {'success': True, 'closed': True}
    return {'success': False, 'error': 'Session not found'}

# Model Management Endpoints (Basic)
@app.get('/api/models/status')
def get_model_status():
    return {
        'total_models': 3,
        'active_models': 1,
        'models': {
            'llama3': {'name': 'llama3', 'size': '8GB', 'loaded': True, 'performance_score': 0.85},
            'phi3': {'name': 'phi3', 'size': '4GB', 'loaded': False, 'performance_score': 0.78},
            'mistral': {'name': 'mistral', 'size': '4GB', 'loaded': False, 'performance_score': 0.82}
        },
        'active_model_names': ['llama3']
    }

@app.post('/api/models/generate')
def generate_with_model(data: dict):
    prompt = data.get('prompt', '')
    model = data.get('model', 'llama3')

    # Simulate AI response
    responses = {
        'llama3': f"Llama3 response to: {prompt[:50]}...",
        'phi3': f"Phi3 (web search) response to: {prompt[:50]}...",
        'mistral': f"Mistral response to: {prompt[:50]}..."
    }

    return {
        'success': True,
        'response': responses.get(model, f"Response to: {prompt[:50]}..."),
        'model': model,
        'response_time': 1.2,
        'token_count': len(prompt.split())
    }

# Data Management Endpoints (Basic)
data_lists = []

@app.post('/api/data/lists')
def create_data_list(data: dict):
    list_id = f"list_{len(data_lists) + 1}"
    new_list = {
        'id': list_id,
        'name': data.get('name', 'New List'),
        'description': data.get('description', ''),
        'type': data.get('list_type', 'general'),
        'items': []
    }
    data_lists.append(new_list)
    return {'success': True, 'result': {'list_id': list_id}}

@app.get('/api/data/lists')
def get_data_lists():
    return {'lists': data_lists}

@app.post('/api/data/lists/items')
def add_data_item(data: dict):
    list_id = data.get('list_id')
    item_data = data.get('data', {})

    for list_item in data_lists:
        if list_item['id'] == list_id:
            item = {
                'id': f"item_{len(list_item['items']) + 1}",
                'data': item_data,
                'source': data.get('source', 'manual'),
                'added_at': '2024-01-01T00:00:00Z'
            }
            list_item['items'].append(item)
            return {'success': True, 'item_id': item['id']}

    return {'success': False, 'error': 'List not found'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
"""
    ]

    return subprocess.Popen(backend_cmd)

def start_frontend():
    """Start the frontend"""
    print("🎨 Starting ToolLlama Frontend...")

    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)

    return subprocess.Popen(['npm', 'run', 'dev'])

def main():
    """Main startup"""
    print("🤖 ToolLlama Quick Start")
    print("=" * 40)

    # Start backend
    backend_process = start_backend()
    time.sleep(2)  # Wait for backend to start

    # Start frontend
    frontend_process = start_frontend()
    time.sleep(3)  # Wait for frontend to start

    print("\n" + "=" * 60)
    print("🎉 ToolLlama Started Successfully!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:5173")
    print("🔧 Backend: http://localhost:8000")
    print("📊 Health: http://localhost:8000/health")
    print("=" * 60)
    print("🧪 Test the system:")
    print("   • Open http://localhost:5173 in your browser")
    print("   • Try the chat interface")
    print("   • Test the data management panels")
    print("=" * 60)

    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

        # Terminate processes
        backend_process.terminate()
        frontend_process.terminate()

        backend_process.wait()
        frontend_process.wait()

        print("✅ Shutdown complete!")

if __name__ == "__main__":
    main()