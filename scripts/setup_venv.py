#!/usr/bin/env python3
"""
ToolLlama Virtual Environment Setup
===================================

Creates a virtual environment and installs all dependencies properly.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def setup_virtual_environment():
    """Set up Python virtual environment"""
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"

    print("🐍 Setting up Python virtual environment...")
    print("=" * 50)

    # Create virtual environment
    if not venv_path.exists():
        if not run_command(f"python3 -m venv {venv_path}", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")

    # Upgrade pip
    pip_cmd = f"{venv_path}/bin/pip"
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False

    # Install backend dependencies
    requirements_file = project_root / "backend" / "requirements.txt"
    if requirements_file.exists():
        if not run_command(f"{pip_cmd} install -r {requirements_file}", "Installing backend dependencies"):
            return False
    else:
        print("⚠️  requirements.txt not found, installing basic dependencies...")
        basic_deps = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "requests",
            "aiohttp",
            "beautifulsoup4",
            "lxml",
            "selenium",
            "playwright",
            "cryptography",
            "oauthlib",
            "google-auth",
            "google-api-python-client"
        ]
        for dep in basic_deps:
            if not run_command(f"{pip_cmd} install {dep}", f"Installing {dep}"):
                print(f"⚠️  Failed to install {dep}, continuing...")

    # Install playwright browsers
    if run_command(f"{venv_path}/bin/playwright install", "Installing Playwright browsers"):
        print("✅ Playwright browsers installed")
    else:
        print("⚠️  Playwright browser installation failed")

    # Create activation script
    activate_script = f"""#!/bin/bash
# ToolLlama Virtual Environment Activator
echo "🐍 Activating ToolLlama virtual environment..."
source {venv_path}/bin/activate
echo "✅ Virtual environment activated!"
echo "📍 You can now run:"
echo "   python start_system.py"
echo "   python test_system.py"
echo "   cd backend && python main.py"
echo ""
echo "🛑 To deactivate: deactivate"
"""

    activator_path = project_root / "activate_venv.sh"
    with open(activator_path, 'w') as f:
        f.write(activate_script)

    # Make activator executable
    os.chmod(activator_path, 0o755)

    print("\n" + "=" * 50)
    print("🎉 Virtual environment setup complete!")
    print("=" * 50)
    print(f"📁 Virtual environment: {venv_path}")
    print(f"🔧 Activator script: {activator_path}")
    print()
    print("🚀 To use ToolLlama:")
    print(f"   source {activator_path}")
    print("   python start_system.py")
    print()
    print("💡 Or run directly:")
    print(f"   {venv_path}/bin/python start_system.py")
    print("=" * 50)

    return True

if __name__ == "__main__":
    success = setup_virtual_environment()
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)