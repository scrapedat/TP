#!/usr/bin/env python3
"""
ToolLlama System Startup Script
===============================

Comprehensive startup script for the entire ToolLlama system including:
- Backend API server
- Frontend development server
- System health checks
- Dependency verification
"""

import subprocess
import sys
import os
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any, List

class SystemStarter:
    """Manages the startup of the entire ToolLlama system"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root
        self.processes = []

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if all required dependencies are available"""
        print("🔍 Checking system dependencies...")

        dependencies = {
            "python": self._check_python_version(),
            "node": self._check_node_version(),
            "ollama": self._check_ollama_running(),
            "backend_deps": self._check_backend_dependencies(),
            "frontend_deps": self._check_frontend_dependencies()
        }

        all_good = all(dependencies.values())

        print("📋 Dependency Check Results:")
        for dep, status in dependencies.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {dep}")

        return dependencies

    def _check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        return version.major >= 3 and version.minor >= 8

    def _check_node_version(self) -> bool:
        """Check Node.js version"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().lstrip('v')
                major_version = int(version.split('.')[0])
                return major_version >= 16
            return False
        except FileNotFoundError:
            return False

    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_backend_dependencies(self) -> bool:
        """Check backend Python dependencies"""
        try:
            import fastapi
            import uvicorn
            import pydantic
            import requests
            return True
        except ImportError:
            return False

    def _check_frontend_dependencies(self) -> bool:
        """Check frontend Node dependencies"""
        package_json = self.frontend_dir / "package.json"
        node_modules = self.frontend_dir / "node_modules"

        if not package_json.exists():
            return False

        # Check if node_modules exists (rough check)
        return node_modules.exists()

    def install_dependencies(self) -> bool:
        """Install missing dependencies"""
        print("📦 Installing dependencies...")

        success = True

        # Install backend dependencies
        if not self._check_backend_dependencies():
            print("   Installing backend dependencies...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r",
                    self.backend_dir / "requirements.txt"
                ], check=True)
                print("   ✅ Backend dependencies installed")
            except subprocess.CalledProcessError:
                print("   ❌ Backend dependency installation failed")
                success = False

        # Install frontend dependencies
        if not self._check_frontend_dependencies():
            print("   Installing frontend dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
                print("   ✅ Frontend dependencies installed")
            except subprocess.CalledProcessError:
                print("   ❌ Frontend dependency installation failed")
                success = False

        return success

    def start_backend(self) -> subprocess.Popen:
        """Start the backend API server"""
        print("🚀 Starting backend server...")

        try:
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ], cwd=self.backend_dir)

            self.processes.append(process)
            print("✅ Backend server started on http://localhost:8000")
            return process
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return None

    def start_frontend(self) -> subprocess.Popen:
        """Start the frontend development server"""
        print("🎨 Starting frontend server...")

        try:
            process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=self.frontend_dir)

            self.processes.append(process)
            print("✅ Frontend server starting...")
            return process
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return None

    def wait_for_services(self) -> Dict[str, bool]:
        """Wait for services to be ready"""
        print("⏳ Waiting for services to be ready...")

        services = {
            "backend": "http://localhost:8000/health",
            "frontend": "http://localhost:5173"
        }

        status = {}
        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            all_ready = True

            for service_name, url in services.items():
                if service_name not in status or not status[service_name]:
                    try:
                        if service_name == "backend":
                            response = requests.get(url, timeout=2)
                            status[service_name] = response.status_code == 200
                        else:
                            # For frontend, just check if port is listening
                            import socket
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            result = sock.connect_ex(('localhost', 5173))
                            status[service_name] = result == 0
                            sock.close()
                    except:
                        status[service_name] = False

                    if not status[service_name]:
                        all_ready = False

            if all_ready:
                break

            attempt += 1
            time.sleep(2)

        return status

    def run_system_tests(self) -> Dict[str, Any]:
        """Run basic system tests"""
        print("🧪 Running system tests...")

        test_results = {
            "backend_health": False,
            "frontend_access": False,
            "api_endpoints": {}
        }

        # Test backend health
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                test_results["backend_health"] = True
                health_data = response.json()
                print(f"   ✅ Backend health: {health_data.get('status', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Backend health check failed: {e}")

        # Test frontend access
        try:
            response = requests.get("http://localhost:5173", timeout=5)
            if response.status_code == 200:
                test_results["frontend_access"] = True
                print("   ✅ Frontend accessible")
        except Exception as e:
            print(f"   ❌ Frontend access failed: {e}")

        # Test key API endpoints
        endpoints_to_test = [
            ("Data lists", "/api/data/lists"),
            ("Web scraping", "/api/tools/scrape_webpage"),
            ("Document extraction", "/api/tools/extract_text")
        ]

        for endpoint_name, endpoint_path in endpoints_to_test:
            try:
                response = requests.get(f"http://localhost:8000{endpoint_path}", timeout=5)
                test_results["api_endpoints"][endpoint_name] = response.status_code == 200
                if response.status_code == 200:
                    print(f"   ✅ {endpoint_name} endpoint accessible")
                else:
                    print(f"   ⚠️  {endpoint_name} endpoint returned {response.status_code}")
            except Exception as e:
                test_results["api_endpoints"][endpoint_name] = False
                print(f"   ❌ {endpoint_name} endpoint failed: {e}")

        return test_results

    def display_startup_info(self):
        """Display comprehensive startup information"""
        print("\n" + "=" * 60)
        print("🎉 ToolLlama System Started Successfully!")
        print("=" * 60)
        print()
        print("🌐 Access Points:")
        print("   📊 Frontend Dashboard: http://localhost:5173")
        print("   🔧 Backend API: http://localhost:8000")
        print("   📚 API Documentation: http://localhost:8000/docs")
        print("   💊 Backend Health: http://localhost:8000/health")
        print()
        print("🎯 Available Panels:")
        print("   💬 Chat - AI conversation with tool integration")
        print("   📊 Data - List management and data storage")
        print("   📧 Communication - Email and messaging tools")
        print("   🌐 Browser - Website automation and login management")
        print("   🔧 Builder - Visual tool creation and workflow design")
        print()
        print("🛠️  Quick Start:")
        print("   1. Open http://localhost:5173 in your browser")
        print("   2. Select a panel from the left navigation")
        print("   3. Start using tools or building custom workflows")
        print()
        print("📋 Example Usage:")
        print("   • Use the Data panel to create lists for URLs, emails, research")
        print("   • Configure browser automation for website logins")
        print("   • Build custom tools with the visual Tool Builder")
        print("   • Integrate everything with Ollama for AI-powered automation")
        print()
        print("🛑 To stop the system:")
        print("   Press Ctrl+C in this terminal")
        print("=" * 60)

    def cleanup(self):
        """Clean up running processes"""
        print("\n🧹 Cleaning up processes...")

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"   ✅ Process {process.pid} terminated")
            except Exception as e:
                print(f"   ⚠️  Error terminating process {process.pid}: {e}")
                try:
                    process.kill()
                except:
                    pass

        self.processes.clear()

    def run(self):
        """Main startup routine"""
        print("🤖 ToolLlama System Startup")
        print("=" * 50)

        try:
            # Step 1: Check dependencies
            deps = self.check_dependencies()
            if not all(deps.values()):
                print("\n⚠️  Some dependencies are missing. Installing...")
                if not self.install_dependencies():
                    print("❌ Dependency installation failed. Please check errors above.")
                    return False

            # Step 2: Start backend
            backend_process = self.start_backend()
            if not backend_process:
                return False

            # Step 3: Start frontend
            frontend_process = self.start_frontend()
            if not frontend_process:
                return False

            # Step 4: Wait for services
            service_status = self.wait_for_services()

            if not all(service_status.values()):
                print("❌ Some services failed to start properly:")
                for service, ready in service_status.items():
                    if not ready:
                        print(f"   ❌ {service} not ready")
                return False

            # Step 5: Run tests
            test_results = self.run_system_tests()

            # Step 6: Display info
            self.display_startup_info()

            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")

        finally:
            self.cleanup()

        return True

def main():
    """Main entry point"""
    starter = SystemStarter()

    try:
        success = starter.run()
        if success:
            print("\n✅ System shutdown complete")
            sys.exit(0)
        else:
            print("\n❌ System startup failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        starter.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()