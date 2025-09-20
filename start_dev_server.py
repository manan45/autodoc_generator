#!/usr/bin/env python3
"""
Development server startup script
Starts both the API server and serves the documentation
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_api_server():
    """Start the API server"""
    print("🚀 Starting API server...")
    return subprocess.Popen([
        sys.executable, 'api_server.py'
    ], cwd=Path(__file__).parent)

def install_dependencies():
    """Install required dependencies"""
    try:
        import flask
        import flask_cors
        print("✅ Dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'flask', 'flask-cors'
        ])

def main():
    """Main startup function"""
    print("🎯 Auto Documentation Generator - Development Server")
    print("=" * 50)
    
    # Install dependencies
    install_dependencies()
    
    # Start API server
    api_process = start_api_server()
    
    print("\n✅ Development server started!")
    print("📊 API Server: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000")
    print("🔍 Repository API: http://localhost:8000/api/repository-data")
    print("🔍 Search API: http://localhost:8000/api/search?q=<query>")
    print("\n💡 Features enabled:")
    print("  • Interactive navigation with clickable links")
    print("  • Repository data integration with vector embeddings")
    print("  • Module complexity analysis and code navigation")
    print("  • Real-time search and similarity matching")
    print("  • Hover tooltips and detailed module modals")
    print("\nPress Ctrl+C to stop the server...")
    
    try:
        # Wait for processes
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
        print("✅ Servers stopped")

if __name__ == '__main__':
    main()
