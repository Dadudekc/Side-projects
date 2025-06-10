#!/usr/bin/env python3
"""
Setup script for VlogForge project.
This script installs dependencies and verifies the environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies from requirements.txt."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def verify_env_file():
    """Verify .env file exists and contains required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found!")
        print("Please create a .env file with the following variables:")
        print("OPENAI_API_KEY=your_key_here")
        print("YOUTUBE_API_KEY=your_key_here")
        print("INSTAGRAM_API_KEY=your_key_here")
        print("TWITTER_API_KEY=your_key_here")
        print("TWITTER_API_SECRET=your_secret_here")
        print("TWITTER_ACCESS_TOKEN=your_token_here")
        print("TWITTER_ACCESS_SECRET=your_secret_here")
        print("MAILCHIMP_API_KEY=your_key_here")
        print("MAILCHIMP_LIST_ID=your_list_id_here")
        return False
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up VlogForge project...")
    
    # Install dependencies
    install_dependencies()
    
    # Verify environment
    if verify_env_file():
        print("✅ Environment verification complete!")
    else:
        print("⚠️  Please set up your environment variables before proceeding.")
    
    print("\n✨ Setup complete! You can now run the verification script:")
    print("python verify_beta.py")

if __name__ == "__main__":
    main() 