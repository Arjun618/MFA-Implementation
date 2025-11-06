#!/usr/bin/env python3
"""
MFA Alignment Pipeline Script
==============================
This script runs the complete forced alignment pipeline using Montreal Forced Aligner.

It performs the following tasks:
1. Validates the prepared corpus
2. Runs forced alignment
3. Organizes output files
4. Generates alignment logs and statistics

Usage:
    python run_alignment.py [--skip-validation] [--clean] [--verbose]
"""

import subprocess
import sys
import argparse
from pathlib import Path
import json
import time
from datetime import datetime


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


def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def check_prerequisites():
    """Check if all prerequisites are met"""
    print_header("Checking Prerequisites")
    
    base_dir = Path(__file__).parent.parent
    corpus_dir = base_dir / "mfa_data" / "corpus"
    
    # Check if corpus exists
    if not corpus_dir.exists():
        print_error("Corpus directory not found!")
        print_info("Run data preparation first:")
        print("  python scripts/prepare_data.py")
        return False
    
    # Check if corpus has files
    audio_files = list(corpus_dir.glob("*.wav"))
    text_files = list(corpus_dir.glob("*.txt"))
    
    print_info(f"Corpus directory: {corpus_dir.relative_to(base_dir)}")
    print_info(f"Audio files: {len(audio_files)}")
    print_info(f"Text files: {len(text_files)}")
    
    if len(audio_files) == 0:
        print_error("No audio files found in corpus!")
        return False
    
    if len(text_files) == 0:
        print_error("No transcript files found in corpus!")
        return False
    
    if len(audio_files) != len(text_files):
        print_warning("Number of audio and text files don't match!")
        print_warning("This may cause alignment issues")
    
    # Check if MFA is installed
    try:
        result = subprocess.run(
            ['mfa', 'version'],
            capture_output=True,
            text=True,
            check=True
        )
        print_success(f"MFA installed: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("MFA is not installed or not in PATH!")
        print_info("Install MFA:")
        print("  conda install -c conda-forge montreal-forced-aligner")
        return False
    
    print_success("\nAll prerequisites met!")
    return True


def validate_corpus(corpus_dir, dictionary, acoustic_model):
    """
    Validate the corpus before alignment
    
    Args:
        corpus_dir: Path to corpus directory
        dictionary: Dictionary name
        acoustic_model: Acoustic model name
    
    Returns:
        bool: True if validation successful
    """
    print_header("Validating Corpus")
    
    print_info("Running MFA validate command...")
    print_info("This checks for OOV words, file issues, and format problems\n")
    
    cmd = [
        'mfa', 'validate',
        str(corpus_dir),
        dictionary,
        acoustic_model,
        '--clean'
    ]
    
    print_info(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print_success("\n✓ Corpus validation successful!")
            return True
        else:
            print_warning("\n⚠ Validation completed with warnings")
            print_info("Proceeding with alignment anyway...")
            return True
            
    except Exception as e:
        print_error(f"Validation error: {e}")
        return False


def run_alignment(corpus_dir, dictionary, acoustic_model, output_dir, args):
    """
    Run forced alignment
    
    Args:
        corpus_dir: Path to corpus directory
        dictionary: Dictionary name
        acoustic_model: Acoustic model name
        output_dir: Output directory for TextGrids
        args: Command line arguments
    
    Returns:
        bool: True if alignment successful
    """
    print_header("Running Forced Alignment")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = [
        'mfa', 'align',
        str(corpus_dir),
        dictionary,
        acoustic_model,
        str(output_dir),
    ]
    
    # Add optional flags
    if args.clean:
        cmd.append('--clean')
    
    if args.verbose:
        cmd.append('--verbose')
    
    # Add beam settings for better alignment
    cmd.extend(['--beam', '100'])
    cmd.extend(['--retry_beam', '400'])
    
    print_info("Alignment Configuration:")
    print(f"  Corpus: {corpus_dir}")
    print(f"  Dictionary: {dictionary}")
    print(f"  Acoustic Model: {acoustic_model}")
    print(f"  Output: {output_dir}")
    print(f"  Beam: 100")
    print(f"  Retry Beam: 400")
    print(f"  Clean: {args.clean}")
    print(f"  Verbose: {args.verbose}")
    
    print_info(f"\nCommand: {' '.join(cmd)}\n")
    print_warning("This may take several minutes depending on audio length...\n")
    
    # Record start time
    start_time = time.time()
    
    try:
        # Run alignment
        result = subprocess.run(cmd, check=False)
        
        # Record end time
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print_success(f"\n✓ Alignment completed successfully!")
            print_info(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            return True
        else:
            print_error(f"\n✗ Alignment failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print_error(f"Alignment error: {e}")
        return False


def check_outputs(output_dir):
    """
    Check alignment outputs
    
    Args:
        output_dir: Output directory
    
    Returns:
        dict: Statistics about outputs
    """
    print_header("Checking Outputs")
    
    textgrid_files = list(output_dir.glob("*.TextGrid"))
    
    stats = {
        'textgrid_count': len(textgrid_files),
        'textgrid_files': [f.name for f in textgrid_files],
        'timestamp': datetime.now().isoformat()
    }
    
    print_info(f"Output directory: {output_dir}")
    print_success(f"Generated TextGrid files: {len(textgrid_files)}")
    
    if textgrid_files:
        print_info("\nGenerated files:")
        for tg_file in sorted(textgrid_files):
            size = tg_file.stat().st_size
            print(f"  - {tg_file.name} ({size:,} bytes)")
    else:
        print_warning("No TextGrid files generated!")
    
    return stats


def save_alignment_log(base_dir, stats, duration):
    """
    Save alignment log and statistics
    
    Args:
        base_dir: Base directory
        stats: Statistics dictionary
        duration: Alignment duration in seconds
    """
    print_header("Saving Alignment Log")
    
    log_dir = base_dir / "outputs" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': duration,
        'duration_minutes': duration / 60,
        'outputs': stats
    }
    
    # Save as JSON
    log_file = log_dir / f"alignment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(log_entry, f, indent=2)
    
    print_success(f"Log saved to: {log_file.relative_to(base_dir)}")
    
    # Also save latest log
    latest_log = log_dir / "latest_alignment.json"
    with open(latest_log, 'w') as f:
        json.dump(log_entry, f, indent=2)
    
    print_success(f"Latest log: {latest_log.relative_to(base_dir)}")


def main():
    """Main function"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Run MFA alignment pipeline')
    parser.add_argument('--skip-validation', action='store_true',
                        help='Skip corpus validation step')
    parser.add_argument('--clean', action='store_true',
                        help='Clean up temporary files after alignment')
    parser.add_argument('--verbose', action='store_true',
                        help='Show verbose output during alignment')
    parser.add_argument('--dictionary', type=str, default='english_us_arpa',
                        help='Pronunciation dictionary to use')
    parser.add_argument('--acoustic-model', type=str, default='english_us_arpa',
                        help='Acoustic model to use')
    
    args = parser.parse_args()
    
    print_header("MFA Alignment Pipeline")
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    corpus_dir = base_dir / "mfa_data" / "corpus"
    output_dir = base_dir / "outputs" / "textgrids"
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Validate corpus (unless skipped)
    if not args.skip_validation:
        if not validate_corpus(corpus_dir, args.dictionary, args.acoustic_model):
            print_error("Validation failed!")
            response = input("\nContinue with alignment anyway? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(1)
    else:
        print_info("Skipping validation (--skip-validation flag used)")
    
    # Run alignment
    start_time = time.time()
    success = run_alignment(corpus_dir, args.dictionary, args.acoustic_model, output_dir, args)
    end_time = time.time()
    duration = end_time - start_time
    
    if not success:
        print_error("\nAlignment failed!")
        sys.exit(1)
    
    # Check outputs
    stats = check_outputs(output_dir)
    
    # Save log
    save_alignment_log(base_dir, stats, duration)
    
    # Final message
    print_header("Pipeline Complete!")
    print_success("Forced alignment completed successfully")
    print_info(f"\nTextGrid files location: {output_dir.relative_to(base_dir)}")
    print_info("\nNext steps:")
    print("  1. View TextGrids in Praat")
    print("  2. Run analysis: python scripts/analyze_outputs.py")
    print("  3. Generate report for submission")
    
    print()


if __name__ == "__main__":
    main()
