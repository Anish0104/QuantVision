import subprocess
import time
import sys
import os

def start_platform():
    print("🚀 Initializing FinVision Pro V5.0...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")
    
    # Start Backend
    print("⚡ Starting FastAPI Backend on http://localhost:8000")
    backend = subprocess.Popen([sys.executable, "main.py"], cwd=project_root)
    
    # Wait for backend
    time.sleep(2)
    
    # Start Frontend
    print("🍀 Starting Next.js Frontend on http://localhost:3000")
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down FinVision...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    start_platform()
