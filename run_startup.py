import subprocess
import time
import sys
import os

def start_platform():
    print("🚀 Initializing FinVision Pro V5.0...")
    
    # Start Backend
    print("⚡ Starting FastAPI Backend on http://localhost:8000")
    backend = subprocess.Popen([sys.executable, "main.py"])
    
    # Wait for backend
    time.sleep(2)
    
    # Start Frontend
    print("🍀 Starting Next.js Frontend on http://localhost:3000")
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd="frontend", shell=True)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down FinVision...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    start_platform()
