#!/usr/bin/env python3
"""
TextGrid Analysis Script
========================
This script analyzes the generated TextGrid files from MFA alignment.

It performs the following tasks:
1. Validates TextGrid file format
2. Extracts word and phoneme statistics
3. Identifies alignment issues (timing, OOV, etc.)
4. Generates visualizations
5. Creates an analysis report

Usage:
    python analyze_outputs.py
"""

import sys
from pathlib import Path
import json
import statistics
from collections import defaultdict
from datetime import datetime

try:
    import textgrid
    TEXTGRID_AVAILABLE = True
except ImportError:
    TEXTGRID_AVAILABLE = False
    print("Warning: textgrid library not available. Install with: pip install textgrid")

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


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


def analyze_textgrid(tg_path):
    """
    Analyze a single TextGrid file
    
    Args:
        tg_path: Path to TextGrid file
    
    Returns:
        dict: Analysis results
    """
    if not TEXTGRID_AVAILABLE:
        return None
    
    try:
        tg = textgrid.TextGrid.fromFile(str(tg_path))
        
        result = {
            'filename': tg_path.name,
            'duration': tg.maxTime,
            'tiers': len(tg.tiers),
            'tier_names': [tier.name for tier in tg.tiers],
            'words': [],
            'phones': [],
            'word_count': 0,
            'phone_count': 0,
            'silence_count': 0,
            'total_speech_time': 0,
            'total_silence_time': 0,
        }
        
        # Analyze each tier
        for tier in tg.tiers:
            tier_name = tier.name.lower()
            
            for interval in tier.intervals:
                duration = interval.maxTime - interval.minTime
                text = interval.mark.strip()
                
                if not text or text == '':
                    continue
                
                # Check if it's a word tier
                if 'word' in tier_name:
                    if text.lower() in ['sp', 'sil', '<sil>', '']:
                        result['silence_count'] += 1
                        result['total_silence_time'] += duration
                    else:
                        result['words'].append({
                            'text': text,
                            'start': interval.minTime,
                            'end': interval.maxTime,
                            'duration': duration
                        })
                        result['word_count'] += 1
                        result['total_speech_time'] += duration
                
                # Check if it's a phone tier
                elif 'phone' in tier_name:
                    if text.lower() in ['sp', 'sil', 'spn', '<sil>', '']:
                        result['silence_count'] += 1
                    else:
                        result['phones'].append({
                            'text': text,
                            'start': interval.minTime,
                            'end': interval.maxTime,
                            'duration': duration
                        })
                        result['phone_count'] += 1
        
        return result
        
    except Exception as e:
        print_error(f"Error analyzing {tg_path.name}: {e}")
        return None


def generate_statistics(analyses):
    """
    Generate overall statistics from all analyses
    
    Args:
        analyses: List of analysis results
    
    Returns:
        dict: Overall statistics
    """
    stats = {
        'total_files': len(analyses),
        'total_duration': 0,
        'total_words': 0,
        'total_phones': 0,
        'total_speech_time': 0,
        'total_silence_time': 0,
        'word_durations': [],
        'phone_durations': [],
        'files': []
    }
    
    for analysis in analyses:
        if not analysis:
            continue
        
        stats['total_duration'] += analysis['duration']
        stats['total_words'] += analysis['word_count']
        stats['total_phones'] += analysis['phone_count']
        stats['total_speech_time'] += analysis['total_speech_time']
        stats['total_silence_time'] += analysis['total_silence_time']
        
        # Collect durations
        for word in analysis['words']:
            stats['word_durations'].append(word['duration'])
        
        for phone in analysis['phones']:
            stats['phone_durations'].append(phone['duration'])
        
        # File-level stats
        stats['files'].append({
            'name': analysis['filename'],
            'duration': analysis['duration'],
            'words': analysis['word_count'],
            'phones': analysis['phone_count']
        })
    
    # Calculate statistics
    if stats['word_durations']:
        stats['word_duration_mean'] = statistics.mean(stats['word_durations'])
        stats['word_duration_median'] = statistics.median(stats['word_durations'])
        stats['word_duration_stdev'] = statistics.stdev(stats['word_durations']) if len(stats['word_durations']) > 1 else 0
        stats['word_duration_min'] = min(stats['word_durations'])
        stats['word_duration_max'] = max(stats['word_durations'])
    
    if stats['phone_durations']:
        stats['phone_duration_mean'] = statistics.mean(stats['phone_durations'])
        stats['phone_duration_median'] = statistics.median(stats['phone_durations'])
        stats['phone_duration_stdev'] = statistics.stdev(stats['phone_durations']) if len(stats['phone_durations']) > 1 else 0
        stats['phone_duration_min'] = min(stats['phone_durations'])
        stats['phone_duration_max'] = max(stats['phone_durations'])
    
    return stats


def print_statistics(stats):
    """Print statistics in a formatted way"""
    print_header("Alignment Statistics")
    
    print(f"{Colors.BOLD}Overall Statistics:{Colors.ENDC}")
    print(f"  Total files analyzed: {stats['total_files']}")
    print(f"  Total audio duration: {stats['total_duration']:.2f} seconds ({stats['total_duration']/60:.2f} minutes)")
    print(f"  Total words aligned: {stats['total_words']}")
    print(f"  Total phonemes aligned: {stats['total_phones']}")
    print(f"  Total speech time: {stats['total_speech_time']:.2f} seconds")
    print(f"  Total silence time: {stats['total_silence_time']:.2f} seconds")
    
    if stats['total_duration'] > 0:
        speech_ratio = (stats['total_speech_time'] / stats['total_duration']) * 100
        print(f"  Speech ratio: {speech_ratio:.1f}%")
    
    if stats.get('word_durations'):
        print(f"\n{Colors.BOLD}Word Duration Statistics:{Colors.ENDC}")
        print(f"  Mean: {stats['word_duration_mean']:.3f} seconds")
        print(f"  Median: {stats['word_duration_median']:.3f} seconds")
        print(f"  Std Dev: {stats['word_duration_stdev']:.3f} seconds")
        print(f"  Min: {stats['word_duration_min']:.3f} seconds")
        print(f"  Max: {stats['word_duration_max']:.3f} seconds")
    
    if stats.get('phone_durations'):
        print(f"\n{Colors.BOLD}Phoneme Duration Statistics:{Colors.ENDC}")
        print(f"  Mean: {stats['phone_duration_mean']:.3f} seconds")
        print(f"  Median: {stats['phone_duration_median']:.3f} seconds")
        print(f"  Std Dev: {stats['phone_duration_stdev']:.3f} seconds")
        print(f"  Min: {stats['phone_duration_min']:.3f} seconds")
        print(f"  Max: {stats['phone_duration_max']:.3f} seconds")
    
    print(f"\n{Colors.BOLD}Per-File Statistics:{Colors.ENDC}")
    for file_stat in stats['files']:
        print(f"  {file_stat['name']}:")
        print(f"    Duration: {file_stat['duration']:.2f}s | Words: {file_stat['words']} | Phones: {file_stat['phones']}")


def identify_issues(analyses):
    """
    Identify potential alignment issues
    
    Args:
        analyses: List of analysis results
    
    Returns:
        list: List of issues found
    """
    issues = []
    
    for analysis in analyses:
        if not analysis:
            continue
        
        filename = analysis['filename']
        
        # Check for very short phonemes (< 20ms)
        short_phones = [p for p in analysis['phones'] if p['duration'] < 0.020]
        if short_phones:
            issues.append({
                'file': filename,
                'type': 'short_phoneme',
                'severity': 'warning',
                'message': f"{len(short_phones)} phonemes shorter than 20ms",
                'details': short_phones[:3]  # First 3 examples
            })
        
        # Check for very long phonemes (> 0.5s)
        long_phones = [p for p in analysis['phones'] if p['duration'] > 0.5]
        if long_phones:
            issues.append({
                'file': filename,
                'type': 'long_phoneme',
                'severity': 'warning',
                'message': f"{len(long_phones)} phonemes longer than 0.5s",
                'details': long_phones[:3]
            })
        
        # Check for very short words (< 50ms)
        short_words = [w for w in analysis['words'] if w['duration'] < 0.050]
        if short_words:
            issues.append({
                'file': filename,
                'type': 'short_word',
                'severity': 'info',
                'message': f"{len(short_words)} words shorter than 50ms",
                'details': short_words[:3]
            })
        
        # Check for very long words (> 2s)
        long_words = [w for w in analysis['words'] if w['duration'] > 2.0]
        if long_words:
            issues.append({
                'file': filename,
                'type': 'long_word',
                'severity': 'warning',
                'message': f"{len(long_words)} words longer than 2s",
                'details': long_words[:3]
            })
    
    return issues


def print_issues(issues):
    """Print identified issues"""
    if not issues:
        print_success("No alignment issues detected!")
        return
    
    print_header("Alignment Issues")
    
    warnings = [i for i in issues if i['severity'] == 'warning']
    infos = [i for i in issues if i['severity'] == 'info']
    
    if warnings:
        print(f"{Colors.WARNING}{Colors.BOLD}Warnings ({len(warnings)}):{Colors.ENDC}")
        for issue in warnings:
            print(f"  {issue['file']}: {issue['message']}")
            if issue.get('details'):
                for detail in issue['details'][:2]:
                    print(f"    - {detail.get('text', 'N/A')}: {detail.get('duration', 0):.3f}s")
    
    if infos:
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}Info ({len(infos)}):{Colors.ENDC}")
        for issue in infos:
            print(f"  {issue['file']}: {issue['message']}")


def create_visualizations(stats, output_dir):
    """
    Create visualization plots
    
    Args:
        stats: Statistics dictionary
        output_dir: Output directory for plots
    """
    if not MATPLOTLIB_AVAILABLE:
        print_warning("Matplotlib not available. Skipping visualizations.")
        return
    
    print_header("Creating Visualizations")
    
    viz_dir = output_dir / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)
    
    # Plot 1: Word duration histogram
    if stats.get('word_durations'):
        plt.figure(figsize=(10, 6))
        plt.hist(stats['word_durations'], bins=50, edgecolor='black', alpha=0.7)
        plt.xlabel('Duration (seconds)')
        plt.ylabel('Frequency')
        plt.title('Word Duration Distribution')
        plt.grid(True, alpha=0.3)
        plot_path = viz_dir / 'word_duration_histogram.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print_success(f"Created: {plot_path.name}")
    
    # Plot 2: Phoneme duration histogram
    if stats.get('phone_durations'):
        plt.figure(figsize=(10, 6))
        plt.hist(stats['phone_durations'], bins=50, edgecolor='black', alpha=0.7, color='orange')
        plt.xlabel('Duration (seconds)')
        plt.ylabel('Frequency')
        plt.title('Phoneme Duration Distribution')
        plt.grid(True, alpha=0.3)
        plot_path = viz_dir / 'phoneme_duration_histogram.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print_success(f"Created: {plot_path.name}")
    
    # Plot 3: Per-file statistics
    if stats.get('files'):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        files = [f['name'][:15] for f in stats['files']]  # Truncate names
        words = [f['words'] for f in stats['files']]
        phones = [f['phones'] for f in stats['files']]
        
        ax1.bar(files, words, color='steelblue')
        ax1.set_xlabel('File')
        ax1.set_ylabel('Word Count')
        ax1.set_title('Words per File')
        ax1.tick_params(axis='x', rotation=45)
        
        ax2.bar(files, phones, color='coral')
        ax2.set_xlabel('File')
        ax2.set_ylabel('Phoneme Count')
        ax2.set_title('Phonemes per File')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plot_path = viz_dir / 'per_file_statistics.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print_success(f"Created: {plot_path.name}")
    
    print_info(f"\nVisualizations saved to: {viz_dir.relative_to(output_dir.parent)}")


def save_analysis_report(stats, issues, output_dir):
    """
    Save analysis report
    
    Args:
        stats: Statistics dictionary
        issues: List of issues
        output_dir: Output directory
    """
    print_header("Saving Analysis Report")
    
    # Save JSON report
    report = {
        'timestamp': datetime.now().isoformat(),
        'statistics': stats,
        'issues': issues
    }
    
    json_path = output_dir / 'analysis_report.json'
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print_success(f"JSON report saved: {json_path.relative_to(output_dir.parent)}")
    
    # Save text report
    txt_path = output_dir / 'analysis_report.txt'
    with open(txt_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("MFA ALIGNMENT ANALYSIS REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("OVERALL STATISTICS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total files: {stats['total_files']}\n")
        f.write(f"Total duration: {stats['total_duration']:.2f}s ({stats['total_duration']/60:.2f}m)\n")
        f.write(f"Total words: {stats['total_words']}\n")
        f.write(f"Total phonemes: {stats['total_phones']}\n\n")
        
        if stats.get('word_durations'):
            f.write("WORD DURATION STATISTICS\n")
            f.write("-" * 60 + "\n")
            f.write(f"Mean: {stats['word_duration_mean']:.3f}s\n")
            f.write(f"Median: {stats['word_duration_median']:.3f}s\n")
            f.write(f"Std Dev: {stats['word_duration_stdev']:.3f}s\n")
            f.write(f"Range: {stats['word_duration_min']:.3f}s - {stats['word_duration_max']:.3f}s\n\n")
        
        if stats.get('phone_durations'):
            f.write("PHONEME DURATION STATISTICS\n")
            f.write("-" * 60 + "\n")
            f.write(f"Mean: {stats['phone_duration_mean']:.3f}s\n")
            f.write(f"Median: {stats['phone_duration_median']:.3f}s\n")
            f.write(f"Std Dev: {stats['phone_duration_stdev']:.3f}s\n")
            f.write(f"Range: {stats['phone_duration_min']:.3f}s - {stats['phone_duration_max']:.3f}s\n\n")
        
        f.write("PER-FILE STATISTICS\n")
        f.write("-" * 60 + "\n")
        for file_stat in stats['files']:
            f.write(f"{file_stat['name']}\n")
            f.write(f"  Duration: {file_stat['duration']:.2f}s\n")
            f.write(f"  Words: {file_stat['words']}\n")
            f.write(f"  Phonemes: {file_stat['phones']}\n\n")
        
        if issues:
            f.write("IDENTIFIED ISSUES\n")
            f.write("-" * 60 + "\n")
            for issue in issues:
                f.write(f"[{issue['severity'].upper()}] {issue['file']}\n")
                f.write(f"  {issue['message']}\n\n")
    
    print_success(f"Text report saved: {txt_path.relative_to(output_dir.parent)}")


def main():
    """Main function"""
    if not TEXTGRID_AVAILABLE:
        print_error("textgrid library is required for analysis")
        print_info("Install with: pip install textgrid")
        sys.exit(1)
    
    print_header("TextGrid Analysis")
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    textgrid_dir = base_dir / "outputs" / "textgrids"
    output_dir = base_dir / "outputs"
    
    # Check if TextGrid directory exists
    if not textgrid_dir.exists():
        print_error(f"TextGrid directory not found: {textgrid_dir}")
        print_info("Run alignment first: python scripts/run_alignment.py")
        sys.exit(1)
    
    # Find TextGrid files
    textgrid_files = list(textgrid_dir.glob("*.TextGrid"))
    
    if not textgrid_files:
        print_error("No TextGrid files found!")
        sys.exit(1)
    
    print_info(f"Found {len(textgrid_files)} TextGrid files\n")
    
    # Analyze each file
    print_info("Analyzing TextGrid files...")
    analyses = []
    
    for tg_file in textgrid_files:
        print(f"  Processing: {tg_file.name}")
        analysis = analyze_textgrid(tg_file)
        if analysis:
            analyses.append(analysis)
            print_success(f"    Words: {analysis['word_count']}, Phones: {analysis['phone_count']}")
    
    if not analyses:
        print_error("No files could be analyzed!")
        sys.exit(1)
    
    print_success(f"\nSuccessfully analyzed {len(analyses)} files")
    
    # Generate statistics
    stats = generate_statistics(analyses)
    
    # Print statistics
    print_statistics(stats)
    
    # Identify issues
    issues = identify_issues(analyses)
    print_issues(issues)
    
    # Create visualizations
    create_visualizations(stats, output_dir)
    
    # Save report
    save_analysis_report(stats, issues, output_dir)
    
    # Final message
    print_header("Analysis Complete!")
    print_success("All analysis tasks completed")
    print_info("\nGenerated files:")
    print(f"  - {output_dir / 'analysis_report.json'}")
    print(f"  - {output_dir / 'analysis_report.txt'}")
    print(f"  - {output_dir / 'visualizations/'}")
    print_info("\nNext steps:")
    print("  1. Review the analysis report")
    print("  2. Check visualizations for patterns")
    print("  3. Open TextGrids in Praat for detailed inspection")
    print("  4. Prepare your PDF report for submission")
    print()


if __name__ == "__main__":
    main()
