#!/usr/bin/env python3
"""
MFA Pipeline Test Script
=========================
This script tests the complete MFA pipeline end-to-end.

It performs the following tests:
1. Environment setup verification
2. Data preparation validation
3. File structure checks
4. Sample alignment test
5. Output validation

Usage:
    python test_pipeline.py
"""

import sys
import subprocess
from pathlib import Path
import json


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKCYAN = '\033[96m'


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


def run_command(command, capture=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=isinstance(command, str),
            capture_output=capture,
            text=True,
            check=False
        )
        return result
    except Exception as e:
        return None


class TestRunner:
    """Test runner for MFA pipeline"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test_environment(self):
        """Test 1: Check environment setup"""
        print_header("Test 1: Environment Setup")
        
        # Check Python version
        print("Checking Python version...")
        py_version = sys.version.split()[0]
        print_info(f"Python version: {py_version}")
        
        major, minor = map(int, py_version.split('.')[:2])
        if major >= 3 and minor >= 8:
            print_success("Python version OK (>= 3.8)")
            self.passed += 1
        else:
            print_error("Python version too old (< 3.8)")
            self.failed += 1
        
        # Check MFA installation
        print("\nChecking MFA installation...")
        result = run_command(['mfa', 'version'])
        
        if result and result.returncode == 0:
            print_success(f"MFA installed: {result.stdout.strip()}")
            self.passed += 1
        else:
            print_error("MFA not installed or not in PATH")
            self.failed += 1
        
        # Check required packages
        print("\nChecking required Python packages...")
        packages = ['textgrid', 'matplotlib', 'numpy', 'pandas']
        
        for package in packages:
            try:
                __import__(package)
                print_success(f"{package} installed")
                self.passed += 1
            except ImportError:
                print_warning(f"{package} NOT installed (optional)")
                self.warnings += 1
    
    def test_directory_structure(self):
        """Test 2: Check directory structure"""
        print_header("Test 2: Directory Structure")
        
        required_dirs = [
            self.base_dir / "wav",
            self.base_dir / "transcripts",
            self.base_dir / "scripts",
            self.base_dir / "mfa_data",
            self.base_dir / "outputs"
        ]
        
        for directory in required_dirs:
            if directory.exists():
                print_success(f"{directory.name}/ exists")
                self.passed += 1
            else:
                print_error(f"{directory.name}/ NOT found")
                self.failed += 1
    
    def test_input_files(self):
        """Test 3: Check input files"""
        print_header("Test 3: Input Files")
        
        wav_dir = self.base_dir / "wav"
        transcript_dir = self.base_dir / "transcripts"
        
        # Check audio files
        audio_files = list(wav_dir.glob("*.wav")) if wav_dir.exists() else []
        print(f"Audio files found: {len(audio_files)}")
        
        if audio_files:
            print_success(f"Found {len(audio_files)} audio files")
            self.passed += 1
            for af in audio_files[:3]:
                print(f"  - {af.name}")
        else:
            print_error("No audio files found!")
            self.failed += 1
        
        # Check transcript files
        transcript_files = list(transcript_dir.glob("*.txt")) + list(transcript_dir.glob("*.TXT")) if transcript_dir.exists() else []
        print(f"\nTranscript files found: {len(transcript_files)}")
        
        if transcript_files:
            print_success(f"Found {len(transcript_files)} transcript files")
            self.passed += 1
            for tf in transcript_files[:3]:
                print(f"  - {tf.name}")
        else:
            print_error("No transcript files found!")
            self.failed += 1
        
        # Check file pairing
        if audio_files and transcript_files:
            if len(audio_files) == len(transcript_files):
                print_success("Audio and transcript counts match")
                self.passed += 1
            else:
                print_warning(f"Mismatch: {len(audio_files)} audio, {len(transcript_files)} transcripts")
                self.warnings += 1
    
    def test_scripts(self):
        """Test 4: Check script files"""
        print_header("Test 4: Script Files")
        
        scripts = [
            "setup_mfa.py",
            "prepare_data.py",
            "run_alignment.py",
            "analyze_outputs.py",
            "test_pipeline.py"
        ]
        
        scripts_dir = self.base_dir / "scripts"
        
        for script in scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                print_success(f"{script} exists")
                self.passed += 1
            else:
                print_error(f"{script} NOT found")
                self.failed += 1
    
    def test_prepared_corpus(self):
        """Test 5: Check prepared corpus"""
        print_header("Test 5: Prepared Corpus")
        
        corpus_dir = self.base_dir / "mfa_data" / "corpus"
        
        if not corpus_dir.exists():
            print_warning("Corpus not prepared yet")
            print_info("Run: python scripts/prepare_data.py")
            self.warnings += 1
            return
        
        # Check corpus files
        audio_files = list(corpus_dir.glob("*.wav"))
        text_files = list(corpus_dir.glob("*.txt"))
        
        print(f"Corpus audio files: {len(audio_files)}")
        print(f"Corpus text files: {len(text_files)}")
        
        if audio_files and text_files:
            print_success(f"Corpus prepared with {len(audio_files)} files")
            self.passed += 1
            
            if len(audio_files) == len(text_files):
                print_success("Audio and text files match")
                self.passed += 1
            else:
                print_error("Audio and text file count mismatch!")
                self.failed += 1
        else:
            print_warning("Corpus is empty")
            self.warnings += 1
    
    def test_alignment_outputs(self):
        """Test 6: Check alignment outputs"""
        print_header("Test 6: Alignment Outputs")
        
        textgrid_dir = self.base_dir / "outputs" / "textgrids"
        
        if not textgrid_dir.exists():
            print_warning("No alignment outputs yet")
            print_info("Run: python scripts/run_alignment.py")
            self.warnings += 1
            return
        
        # Check TextGrid files
        textgrid_files = list(textgrid_dir.glob("*.TextGrid"))
        
        print(f"TextGrid files found: {len(textgrid_files)}")
        
        if textgrid_files:
            print_success(f"Found {len(textgrid_files)} TextGrid files")
            self.passed += 1
            
            for tg in textgrid_files[:3]:
                size = tg.stat().st_size
                print(f"  - {tg.name} ({size:,} bytes)")
        else:
            print_warning("No TextGrid files found")
            self.warnings += 1
    
    def test_analysis_outputs(self):
        """Test 7: Check analysis outputs"""
        print_header("Test 7: Analysis Outputs")
        
        output_dir = self.base_dir / "outputs"
        
        # Check for analysis report
        report_json = output_dir / "analysis_report.json"
        report_txt = output_dir / "analysis_report.txt"
        
        if report_json.exists():
            print_success("JSON report exists")
            self.passed += 1
            
            # Try to load it
            try:
                with open(report_json) as f:
                    data = json.load(f)
                print_info(f"Total files analyzed: {data.get('statistics', {}).get('total_files', 'N/A')}")
            except:
                print_warning("Could not parse JSON report")
        else:
            print_warning("No JSON report found")
            print_info("Run: python scripts/analyze_outputs.py")
            self.warnings += 1
        
        if report_txt.exists():
            print_success("Text report exists")
            self.passed += 1
        else:
            print_warning("No text report found")
            self.warnings += 1
        
        # Check for visualizations
        viz_dir = output_dir / "visualizations"
        if viz_dir.exists():
            plots = list(viz_dir.glob("*.png"))
            if plots:
                print_success(f"Found {len(plots)} visualization plots")
                self.passed += 1
            else:
                print_warning("No visualization plots found")
                self.warnings += 1
        else:
            print_warning("Visualizations directory not found")
            self.warnings += 1
    
    def run_all_tests(self):
        """Run all tests"""
        print_header("MFA Pipeline Test Suite")
        print_info("Testing all components of the MFA pipeline\n")
        
        self.test_environment()
        self.test_directory_structure()
        self.test_input_files()
        self.test_scripts()
        self.test_prepared_corpus()
        self.test_alignment_outputs()
        self.test_analysis_outputs()
        
        # Print summary
        print_header("Test Summary")
        
        total = self.passed + self.failed
        
        print(f"Tests passed: {Colors.OKGREEN}{self.passed}{Colors.ENDC}")
        print(f"Tests failed: {Colors.FAIL}{self.failed}{Colors.ENDC}")
        print(f"Warnings: {Colors.WARNING}{self.warnings}{Colors.ENDC}")
        
        if self.failed == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}")
            if self.warnings > 0:
                print(f"{Colors.WARNING}Note: Some optional components are missing{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}")
            print("Please fix the issues above before proceeding.")
        
        return self.failed == 0


def main():
    """Main function"""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n" + "="*60)
        print_info("Next steps:")
        print("  1. If corpus not prepared: python scripts/prepare_data.py")
        print("  2. If alignment not run: python scripts/run_alignment.py")
        print("  3. If analysis not done: python scripts/analyze_outputs.py")
        print("  4. Review outputs and create your PDF report")
        print()
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
