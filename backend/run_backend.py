#!/usr/bin/env python3
"""
ToolLlama Backend Runner
========================

Simple script to run the ToolLlama backend API server.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the FastAPI backend server"""

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("🚀 Starting ToolLlama Backend API Server")
    print("=" * 50)
    print(f"📁 Working directory: {backend_dir}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("=" * 50)

    try:
        # Run uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()