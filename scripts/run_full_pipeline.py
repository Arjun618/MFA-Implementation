#!/usr/bin/env python3
"""
Master Pipeline Runner
======================
This script runs the complete MFA pipeline from start to finish.

Usage:
    python run_full_pipeline.py [--skip-tests] [--skip-validation]
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time


class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def run_script(script_name, description):
    """Run a Python script"""
    print_header(description)
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print_error(f"Script not found: {script_name}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False
        )
        
        if result.returncode == 0:
            print_success(f"{description} completed successfully")
            return True
        else:
            print_error(f"{description} failed with code {result.returncode}")
            return False
    except Exception as e:
        print_error(f"Error running {script_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run complete MFA pipeline')
    parser.add_argument('--skip-tests', action='store_true', help='Skip initial tests')
    parser.add_argument('--skip-validation', action='store_true', help='Skip corpus validation')
    args = parser.parse_args()
    
    print_header("MFA COMPLETE PIPELINE")
    print("This will run all steps from setup to analysis")
    print()
    
    start_time = time.time()
    
    # Step 1: Run tests (optional)
    if not args.skip_tests:
        if not run_script("test_pipeline.py", "Step 1: Testing Environment"):
            print_error("\nTests failed! Fix issues before continuing.")
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(1)
    else:
        print("Skipping tests (--skip-tests flag)")
    
    # Step 2: Setup (optional, may already be done)
    print_header("Step 2: Environment Setup")
    print("If you haven't set up MFA yet, run: python scripts/setup_mfa.py")
    print("Skipping automated setup (assumed already done)")
    
    # Step 3: Prepare data
    if not run_script("prepare_data.py", "Step 3: Preparing Data"):
        print_error("\nData preparation failed!")
        sys.exit(1)
    
    # Step 4: Run alignment
    if not run_script("run_alignment.py", "Step 4: Running Alignment"):
        print_error("\nAlignment failed!")
        sys.exit(1)
    
    # Step 5: Analyze outputs
    if not run_script("analyze_outputs.py", "Step 5: Analyzing Outputs"):
        print_error("\nAnalysis failed!")
        sys.exit(1)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Final summary
    print_header("PIPELINE COMPLETE!")
    print_success("All steps completed successfully")
    print(f"\nTotal time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("  1. Check outputs/textgrids/ for TextGrid files")
    print("  2. Open TextGrids in Praat for visual inspection")
    print("  3. Review outputs/analysis_report.txt")
    print("  4. Check outputs/visualizations/ for plots")
    print("  5. Fill in docs/report_template.md with your findings")
    print("  6. Convert report to PDF for submission")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
