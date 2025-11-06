#!/usr/bin/env python3
"""
MFA Setup Script
================
This script automates the setup of Montreal Forced Aligner (MFA) environment.

It performs the following tasks:
1. Verifies MFA installation
2. Downloads required acoustic models
3. Downloads pronunciation dictionaries
4. Validates the environment setup

Usage:
    python setup_mfa.py
"""

import subprocess
import sys
import os
import json
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message):
    """Print a formatted header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message):
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def run_command(command, check=True, capture_output=True):
    """
    Run a shell command and return the result
    
    Args:
        command: Command to run (string or list)
        check: Whether to raise exception on error
        capture_output: Whether to capture stdout/stderr
    
    Returns:
        CompletedProcess object
    """
    if isinstance(command, str):
        command = command.split()
    
    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {' '.join(command)}")
            print_error(f"Error: {e.stderr}")
        return None
    except FileNotFoundError:
        if check:
            print_error(f"Command not found: {command[0]}")
        return None


def check_mfa_installation():
    """Check if MFA is installed and get version"""
    print_header("Step 1: Checking MFA Installation")
    
    result = run_command("mfa version", check=False)
    
    if result and result.returncode == 0:
        version = result.stdout.strip()
        print_success(f"MFA is installed: {version}")
        return True
    else:
        print_error("MFA is not installed or not in PATH")
        print_info("Please install MFA using one of the following methods:")
        print("  1. conda install -c conda-forge montreal-forced-aligner")
        print("  2. pip install montreal-forced-aligner")
        return False


def check_conda_environment():
    """Check if running in a conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print_success(f"Running in conda environment: {conda_env}")
        return True
    else:
        print_warning("Not running in a conda environment")
        print_info("Recommended: Create a conda environment for MFA")
        print("  conda create -n mfa python=3.10 -y")
        print("  conda activate mfa")
        return False


def list_available_models():
    """List all available MFA models"""
    print_header("Step 2: Checking Available Models")
    
    print_info("Fetching available acoustic models...")
    result = run_command("mfa model download acoustic --ignore_cache", check=False)
    
    if result and result.returncode == 0:
        print_success("Available acoustic models:")
        print(result.stdout)
    else:
        print_warning("Could not fetch acoustic models list")
    
    print_info("\nFetching available dictionaries...")
    result = run_command("mfa model download dictionary --ignore_cache", check=False)
    
    if result and result.returncode == 0:
        print_success("Available dictionaries:")
        print(result.stdout)
    else:
        print_warning("Could not fetch dictionary list")


def download_models():
    """Download required acoustic models and dictionaries"""
    print_header("Step 3: Downloading Required Models")
    
    models = [
        ("acoustic", "english_us_arpa", "US English acoustic model"),
        ("dictionary", "english_us_arpa", "US English pronunciation dictionary"),
    ]
    
    for model_type, model_name, description in models:
        print_info(f"Downloading {description}...")
        result = run_command(
            f"mfa model download {model_type} {model_name}",
            check=False
        )
        
        if result and result.returncode == 0:
            print_success(f"Downloaded {model_name}")
        else:
            print_warning(f"Could not download {model_name} (may already exist)")


def list_installed_models():
    """List installed MFA models"""
    print_header("Step 4: Verifying Installed Models")
    
    print_info("Installed models:")
    result = run_command("mfa model list", check=False)
    
    if result and result.returncode == 0:
        print(result.stdout)
        print_success("Models verified")
    else:
        print_error("Could not list installed models")


def create_directories():
    """Create necessary directories for the project"""
    print_header("Step 5: Creating Project Directories")
    
    base_dir = Path(__file__).parent.parent
    directories = [
        base_dir / "mfa_data" / "corpus",
        base_dir / "outputs" / "textgrids",
        base_dir / "outputs" / "logs",
        base_dir / "outputs" / "visualizations",
        base_dir / "docs",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"Created/verified: {directory.relative_to(base_dir)}")


def check_dependencies():
    """Check for required Python packages"""
    print_header("Step 6: Checking Python Dependencies")
    
    required_packages = [
        "textgrid",
        "matplotlib",
        "numpy",
        "pandas",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_warning(f"{package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print_info("\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing_packages)}")
        print("  OR")
        print(f"  pip install -r requirements.txt")
        return False
    else:
        print_success("\nAll required packages are installed")
        return True


def save_setup_info():
    """Save setup information to a JSON file"""
    print_header("Step 7: Saving Setup Information")
    
    base_dir = Path(__file__).parent.parent
    setup_info = {
        "mfa_installed": True,
        "conda_env": os.environ.get('CONDA_DEFAULT_ENV', 'None'),
        "python_version": sys.version.split()[0],
        "models": {
            "acoustic": "english_us_arpa",
            "dictionary": "english_us_arpa"
        },
        "directories": {
            "corpus": str(base_dir / "mfa_data" / "corpus"),
            "outputs": str(base_dir / "outputs"),
            "textgrids": str(base_dir / "outputs" / "textgrids"),
        }
    }
    
    setup_file = base_dir / "outputs" / "setup_info.json"
    with open(setup_file, 'w') as f:
        json.dump(setup_info, f, indent=2)
    
    print_success(f"Setup info saved to: {setup_file.relative_to(base_dir)}")


def main():
    """Main setup function"""
    print_header("MFA Setup Script")
    print_info("This script will set up your MFA environment\n")
    
    # Check conda environment
    check_conda_environment()
    
    # Check MFA installation
    if not check_mfa_installation():
        print_error("\nSetup cannot continue without MFA installed")
        sys.exit(1)
    
    # List available models (optional)
    # list_available_models()
    
    # Download required models
    download_models()
    
    # List installed models
    list_installed_models()
    
    # Create directories
    create_directories()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Save setup info
    save_setup_info()
    
    # Final summary
    print_header("Setup Complete!")
    print_success("MFA environment is ready")
    print_info("\nNext steps:")
    print("  1. Run: python scripts/prepare_data.py")
    print("  2. Run: python scripts/run_alignment.py")
    print("  3. Run: python scripts/analyze_outputs.py")
    
    if not deps_ok:
        print_warning("\nNote: Some Python packages are missing. Install them before proceeding.")
    
    print()


if __name__ == "__main__":
    main()
