#!/usr/bin/env python3
"""
Data Preparation Script for MFA
================================
This script prepares audio and transcript data for Montreal Forced Aligner.

It performs the following tasks:
1. Validates audio files (format, sample rate, channels)
2. Normalizes transcript filenames to match audio files
3. Cleans and formats transcript text
4. Organizes files in MFA-required structure
5. Generates a validation report

Usage:
    python prepare_data.py
"""

import os
import shutil
import re
from pathlib import Path
import subprocess


class Colors:
    """ANSI color codes for terminal output"""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKCYAN = '\033[96m'


def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_header(message):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def get_audio_info(audio_path):
    """
    Get audio file information using ffprobe
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        dict with sample_rate, channels, duration, format
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        import json
        data = json.loads(result.stdout)
        
        audio_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        if audio_stream:
            return {
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'duration': float(data.get('format', {}).get('duration', 0)),
                'format': data.get('format', {}).get('format_name', 'unknown')
            }
    except Exception as e:
        print_warning(f"Could not get audio info for {audio_path.name}: {e}")
    
    return None


def clean_transcript_text(text):
    """
    Clean and normalize transcript text for MFA
    
    Args:
        text: Raw transcript text
    
    Returns:
        Cleaned text string
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Convert to uppercase (MFA prefers uppercase for some dictionaries)
    # Comment this out if you want to preserve case
    # text = text.upper()
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def prepare_corpus():
    """
    Prepare the corpus for MFA alignment
    
    This function:
    1. Copies audio files to mfa_data/corpus
    2. Creates matching transcript files (.txt)
    3. Validates file pairs
    """
    print_header("Data Preparation for MFA")
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    wav_dir = base_dir / "wav"
    transcript_dir = base_dir / "transcripts"
    corpus_dir = base_dir / "mfa_data" / "corpus"
    
    # Create corpus directory
    corpus_dir.mkdir(parents=True, exist_ok=True)
    
    # Get list of audio files
    audio_files = sorted(wav_dir.glob("*.wav"))
    
    if not audio_files:
        print_error(f"No audio files found in {wav_dir}")
        return False
    
    print_info(f"Found {len(audio_files)} audio files\n")
    
    # Track statistics
    stats = {
        'total_files': 0,
        'successful': 0,
        'failed': 0,
        'missing_transcripts': 0,
        'audio_issues': 0
    }
    
    # Process each audio file
    for audio_path in audio_files:
        stats['total_files'] += 1
        audio_name = audio_path.stem
        
        print(f"\nProcessing: {audio_path.name}")
        
        # Find matching transcript
        # Try different case variations
        transcript_candidates = [
            transcript_dir / f"{audio_name}.txt",
            transcript_dir / f"{audio_name}.TXT",
            transcript_dir / f"{audio_name.upper()}.txt",
            transcript_dir / f"{audio_name.upper()}.TXT",
            transcript_dir / f"{audio_name.lower()}.txt",
        ]
        
        transcript_path = None
        for candidate in transcript_candidates:
            if candidate.exists():
                transcript_path = candidate
                break
        
        if not transcript_path:
            print_error(f"  No transcript found for {audio_name}")
            stats['missing_transcripts'] += 1
            stats['failed'] += 1
            continue
        
        print_success(f"  Found transcript: {transcript_path.name}")
        
        # Get audio info
        audio_info = get_audio_info(audio_path)
        if audio_info:
            print_info(f"  Sample rate: {audio_info['sample_rate']} Hz")
            print_info(f"  Channels: {audio_info['channels']}")
            print_info(f"  Duration: {audio_info['duration']:.2f} seconds")
            
            # Check audio format
            if audio_info['sample_rate'] < 16000:
                print_warning(f"  Low sample rate (< 16kHz) may affect alignment quality")
            
            if audio_info['channels'] > 1:
                print_warning(f"  Multi-channel audio - MFA prefers mono")
        
        # Read and clean transcript
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            cleaned_text = clean_transcript_text(transcript_text)
            
            if not cleaned_text:
                print_error(f"  Empty transcript after cleaning")
                stats['failed'] += 1
                continue
            
            print_info(f"  Transcript length: {len(cleaned_text)} characters")
            print_info(f"  Preview: {cleaned_text[:60]}...")
            
            # Copy audio file to corpus
            dest_audio = corpus_dir / audio_path.name
            shutil.copy2(audio_path, dest_audio)
            print_success(f"  Copied audio to corpus")
            
            # Create matching transcript file (same name, .txt extension)
            dest_transcript = corpus_dir / f"{audio_path.stem}.txt"
            with open(dest_transcript, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            print_success(f"  Created transcript: {dest_transcript.name}")
            
            stats['successful'] += 1
            
        except Exception as e:
            print_error(f"  Error processing: {e}")
            stats['failed'] += 1
    
    # Print summary
    print_header("Preparation Summary")
    print(f"Total files processed: {stats['total_files']}")
    print_success(f"Successfully prepared: {stats['successful']}")
    if stats['failed'] > 0:
        print_error(f"Failed: {stats['failed']}")
    if stats['missing_transcripts'] > 0:
        print_warning(f"Missing transcripts: {stats['missing_transcripts']}")
    
    print_info(f"\nCorpus directory: {corpus_dir.relative_to(base_dir)}")
    
    # List files in corpus
    corpus_files = list(corpus_dir.glob("*"))
    print_info(f"Files in corpus: {len(corpus_files)}")
    
    audio_files_corpus = list(corpus_dir.glob("*.wav"))
    txt_files_corpus = list(corpus_dir.glob("*.txt"))
    
    print(f"  - Audio files (.wav): {len(audio_files_corpus)}")
    print(f"  - Transcript files (.txt): {len(txt_files_corpus)}")
    
    if len(audio_files_corpus) != len(txt_files_corpus):
        print_error("\n⚠️  WARNING: Number of audio and transcript files don't match!")
        return False
    
    print_success("\n✓ Data preparation complete!")
    print_info("\nNext step: Run alignment with:")
    print(f"  python scripts/run_alignment.py")
    print(f"  OR")
    print(f"  mfa align {corpus_dir} english_us_arpa english_us_arpa outputs/textgrids")
    
    return True


def validate_corpus():
    """
    Validate the prepared corpus using MFA validate command
    """
    print_header("Validating Corpus with MFA")
    
    base_dir = Path(__file__).parent.parent
    corpus_dir = base_dir / "mfa_data" / "corpus"
    
    if not corpus_dir.exists():
        print_error(f"Corpus directory not found: {corpus_dir}")
        print_info("Run data preparation first: python scripts/prepare_data.py")
        return False
    
    print_info("Running MFA validation...")
    print_info("This will check for:")
    print("  - Missing audio or transcript files")
    print("  - Out-of-vocabulary (OOV) words")
    print("  - Audio format issues\n")
    
    cmd = [
        'mfa', 'validate',
        str(corpus_dir),
        'english_us_arpa',  # dictionary
        'english_us_arpa',  # acoustic model
        '--clean'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print_success("\n✓ Corpus validation successful!")
            return True
        else:
            print_warning("\n⚠ Validation completed with warnings")
            print_info("Check the output above for details")
            return True
            
    except FileNotFoundError:
        print_error("MFA command not found")
        print_info("Make sure MFA is installed and in your PATH")
        print_info("  conda install -c conda-forge montreal-forced-aligner")
        return False
    except Exception as e:
        print_error(f"Validation error: {e}")
        return False


def main():
    """Main function"""
    # Prepare data
    success = prepare_corpus()
    
    if not success:
        print_error("\nData preparation failed!")
        return
    
    # Ask if user wants to validate
    print("\n" + "="*60)
    response = input("Do you want to validate the corpus with MFA? (y/n): ").strip().lower()
    
    if response == 'y':
        validate_corpus()
    else:
        print_info("Skipping validation. You can run it later with:")
        print("  mfa validate mfa_data/corpus english_us_arpa english_us_arpa")


if __name__ == "__main__":
    main()
