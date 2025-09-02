#!/usr/bin/env python3
"""
Startup script for the Calorie Tracker frontend
"""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

def main():
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    print("🌐 Starting Calorie Tracker Frontend...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if index.html exists
    if not (frontend_dir / "index.html").exists():
        print("❌ index.html not found in frontend directory!")
        return 1
    
    # Start HTTP server
    port = 8080
    print(f"🚀 Starting HTTP server on port {port}...")
    print(f"📍 Frontend will be available at: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open(f"http://localhost:{port}")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Use Python's built-in HTTP server
        subprocess.run([sys.executable, "-m", "http.server", str(port)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
