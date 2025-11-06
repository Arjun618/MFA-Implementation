# Montreal Forced Aligner (MFA) Assignment

This repository contains a complete implementation of forced alignment using the Montreal Forced Aligner (MFA) tool for speech audio and phonetic transcription.

## 📋 Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Dataset](#dataset)
- [Usage](#usage)
- [Output Analysis](#output-analysis)
- [Observations](#observations)
- [Resources](#resources)

## 🎯 Overview

**Forced alignment** is the process of automatically matching an audio recording with its corresponding text transcription at the word and phoneme level. This project uses the Montreal Forced Aligner (MFA) to:

1. Align speech audio with text transcripts
2. Generate word and phoneme boundaries
3. Produce TextGrid files for visualization in Praat
4. Analyze alignment quality and timing accuracy

## 📁 Project Structure

```
Assignment/
├── README.md                    # This file
├── objective.txt                # Assignment requirements
├── wav/                         # Audio files (.wav)
├── transcripts/                 # Text transcripts (.txt)
├── mfa_data/                    # MFA-formatted data directory
├── outputs/                     # Generated TextGrid files and logs
├── scripts/                     # Python automation scripts
│   ├── setup_mfa.py            # MFA installation script
│   ├── prepare_data.py         # Data preparation script
│   ├── run_alignment.py        # Alignment pipeline script
│   ├── analyze_outputs.py      # Output validation and analysis
│   └── test_pipeline.py        # End-to-end testing script
```

## 🔧 Prerequisites

- **Operating System**: macOS, Linux, or Windows (WSL recommended)
- **Python**: 3.8 or higher
- **Conda**: Recommended for environment management
- **Praat**: For viewing TextGrid files (optional but recommended)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Arjun618/MFA-Implementation
```

### Step 2: Create Conda Environment

```bash
# Create a new conda environment
conda create -n mfa python=3.10 -y

# Activate the environment
conda activate mfa
```

### Step 3: Install Montreal Forced Aligner

```bash
# Install MFA via conda (recommended)
conda install -c conda-forge montreal-forced-aligner

# Verify installation
mfa version
```

**Alternative installation via pip:**
```bash
pip install montreal-forced-aligner
```

### Step 4: Install Required Python Packages

```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install textgrid matplotlib numpy pandas
```

### Step 5: Run Setup Script (Automated)

```bash
python scripts/setup_mfa.py
```

This script will:
- Verify MFA installation
- Download required acoustic models
- Download pronunciation dictionary
- Set up the environment

## 📊 Dataset

The dataset contains 6 audio files with corresponding transcripts:

| Audio File | Transcript File | Type |
|------------|----------------|------|
| F2BJRLP1.wav | F2BJRLP1.TXT | Long-form speech |
| F2BJRLP2.wav | F2BJRLP2.TXT | Long-form speech |
| F2BJRLP3.wav | F2BJRLP3.TXT | Long-form speech |
| ISLE_SESS0131_BLOCKD02_01_sprt1.wav | ISLE_SESS0131_BLOCKD02_01_sprt1.txt | Short utterance |
| ISLE_SESS0131_BLOCKD02_02_sprt1.wav | ISLE_SESS0131_BLOCKD02_02_sprt1.txt | Short utterance |
| ISLE_SESS0131_BLOCKD02_03_sprt1.wav | ISLE_SESS0131_BLOCKD02_03_sprt1.txt | Short utterance |

## 📝 Usage

### Quick Start (Automated Pipeline)

Run the complete pipeline with a single command:

```bash
# Activate the conda environment
conda activate mfa

# Run the complete pipeline
python scripts/run_alignment.py
```

### Step-by-Step Manual Process

#### 1. Prepare Data

```bash
python scripts/prepare_data.py
```

This script:
- Copies audio files to `mfa_data/corpus`
- Normalizes transcript filenames (must match audio files)
- Validates file pairing
- Cleans text formatting

#### 2. Download Models (if not done in setup)

```bash
# Download acoustic model
mfa model download acoustic english_us_arpa

# Download pronunciation dictionary
mfa model download dictionary english_us_arpa

# List available models
mfa model list
```

#### 3. Validate Data

```bash
# Validate corpus before alignment
mfa validate mfa_data/corpus english_us_arpa english_us_arpa
```

This checks for:
- Missing audio or transcript files
- Out-of-vocabulary (OOV) words
- Audio format issues

#### 4. Run Forced Alignment

```bash
# Run alignment
mfa align mfa_data/corpus english_us_arpa english_us_arpa outputs/textgrids

# With custom options
mfa align mfa_data/corpus english_us_arpa english_us_arpa outputs/textgrids \
    --clean \
    --verbose \
    --beam 100 \
    --retry_beam 400
```

**Parameters:**
- `mfa_data/corpus`: Input directory with audio and transcripts
- `english_us_arpa`: Pronunciation dictionary
- `english_us_arpa`: Acoustic model
- `outputs/textgrids`: Output directory for TextGrid files
- `--clean`: Clean up temporary files
- `--verbose`: Show detailed progress
- `--beam`: Beam width for decoding (higher = more accurate but slower)

#### 5. Analyze Outputs

```bash
python scripts/analyze_outputs.py
```

This script:
- Validates TextGrid files
- Extracts alignment statistics
- Generates visualization plots
- Identifies alignment issues

#### 6. Test the Pipeline

```bash
python scripts/test_pipeline.py
```

Runs end-to-end tests to verify everything works correctly.

### View Results in Praat

1. **Install Praat**: Download from [praat.org](https://www.praat.org/)
2. **Open TextGrid**:
   - Open Praat
   - Click "Open" → "Read from file"
   - Select a TextGrid file from `outputs/textgrids/`
   - Also open the corresponding WAV file
   - Select both and click "View & Edit"
3. **Explore**:
   - View word and phoneme tiers
   - Listen to aligned segments
   - Check timing accuracy

## 📈 Output Analysis

### Generated Files

After alignment, you'll find:

```
outputs/
├── textgrids/                  # TextGrid files (one per audio)
│   ├── F2BJRLP1.TextGrid
│   ├── F2BJRLP2.TextGrid
│   └── ...
├── alignment_stats.json        # Statistics and metrics
├── analysis_report.txt         # Detailed analysis report
└── visualizations/             # Plots and charts
    ├── phoneme_durations.png
    ├── word_durations.png
    └── alignment_quality.png
```

### Key Metrics

- **Total words aligned**: Count of successfully aligned words
- **Total phonemes aligned**: Count of successfully aligned phonemes
- **Average word duration**: Mean duration of words in seconds
- **Average phoneme duration**: Mean duration of phonemes in seconds
- **OOV words**: Out-of-vocabulary words that couldn't be aligned
- **Silence regions**: Detected pauses and silence

## 🔍 Observations

### Expected Observations

1. **Word Boundaries**: Clear demarcation of word start and end times
2. **Phoneme Boundaries**: Individual phoneme segments with timing
3. **Silence Handling**: MFA detects and marks silence/pauses
4. **Pronunciation Variants**: Some words may have multiple pronunciations

### Common Issues

1. **OOV Words**: Words not in the dictionary won't align
   - Solution: Add custom pronunciations or use G2P model
2. **Background Noise**: May affect alignment quality
   - Solution: Use better quality audio or noise reduction
3. **Fast Speech**: Rapid speech may have timing offsets
   - Solution: Adjust beam parameters
4. **Transcript Mismatch**: Transcripts must exactly match audio
   - Solution: Verify and correct transcripts

### Quality Indicators

- ✅ **Good alignment**: Words and phonemes have reasonable durations
- ⚠️ **Warning**: Very short (<20ms) or very long (>2s) phoneme durations
- ❌ **Poor alignment**: Missing segments or large timing offsets

## 📚 Resources

### MFA Documentation
- [Official Documentation](https://montreal-forced-aligner.readthedocs.io/)
- [GitHub Repository](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner)
- [Tutorial Videos](https://memcauliffe.com/mfa-videos.html)

### Praat
- [Download Praat](https://www.praat.org/)
- [Praat Manual](https://www.fon.hum.uva.nl/praat/manual/)

### Phonetics Resources
- [ARPAbet Phoneme Set](https://en.wikipedia.org/wiki/ARPABET)
- [IPA Chart](https://www.internationalphoneticassociation.org/content/ipa-chart)

## 🎓 Extra Credit Opportunities

1. **Train Custom Dictionary**: Use G2P model to generate pronunciations
   ```bash
   mfa g2p english_us_arpa mfa_data/corpus outputs/custom_dict.txt
   ```

2. **Try Multiple Models**: Compare different acoustic models
   ```bash
   mfa model download acoustic english_mfa
   mfa align mfa_data/corpus english_us_arpa english_mfa outputs/textgrids_mfa
   ```

3. **Automated Pipeline**: Create a full automation script (see `scripts/run_alignment.py`)

4. **Custom Visualization**: Generate plots of alignment results

## 📧 Submission Checklist

- [x] GitHub repository with all scripts
- [x] README.md with clear instructions
- [x] Generated TextGrid files in outputs/
- [x] All links publicly accessible
- [x] Requirements.txt with dependencies
- [x] Sample commands documented

## 🐛 Troubleshooting

### MFA Command Not Found
```bash
# Ensure conda environment is activated
conda activate mfa
which mfa
```

### Permission Errors
```bash
# On macOS, you may need to allow terminal access
# System Preferences → Security & Privacy → Privacy → Full Disk Access
```

### Audio Format Issues
```bash
# MFA requires 16kHz mono WAV files
# Convert if needed:
ffmpeg -i input.wav -ar 16000 -ac 1 output.wav
```

### Out of Memory
```bash
# Reduce beam width or process files individually
mfa align mfa_data/corpus english_us_arpa english_us_arpa outputs/textgrids --beam 50
```

---

**Last Updated**: November 4, 2025
