# MFA Forced Alignment Report

**Student Name:** [Your Name]  
**Course:** IIIT Hyderabad - Speech Processing  
**Assignment:** Assignment 1 - Forced Alignment using Montreal Forced Aligner  
**Date:** November 4, 2025

---

## 1. Executive Summary

This report presents the results of implementing a complete forced alignment pipeline using the Montreal Forced Aligner (MFA) tool. The project involved setting up the MFA environment, preparing audio and transcript data, running forced alignment, and analyzing the results.

**Key Achievements:**
- Successfully aligned [X] audio files with their transcripts
- Generated [X] TextGrid files with word and phoneme boundaries
- Identified [X] words and [Y] phonemes with precise timing information
- Analyzed alignment quality and identified potential issues

---

## 2. Introduction

### 2.1 What is Forced Alignment?

Forced alignment is an automated process that synchronizes audio recordings with their corresponding text transcriptions at the word and phoneme level. It determines the exact start and end times for each linguistic unit in the speech signal.

### 2.2 Objective

The objective of this assignment was to:
1. Set up the Montreal Forced Aligner environment
2. Prepare audio and transcript data in MFA-compatible format
3. Run forced alignment on provided dataset
4. Analyze and visualize alignment results
5. Identify alignment quality and potential issues

---

## 3. Methodology

### 3.1 Environment Setup

**System Configuration:**
- Operating System: macOS [version]
- Python Version: 3.10
- MFA Version: [X.X.X]
- Installation Method: Conda

**Installation Steps:**
```bash
conda create -n mfa python=3.10 -y
conda activate mfa
conda install -c conda-forge montreal-forced-aligner
```

### 3.2 Dataset

The dataset consisted of 6 audio-transcript pairs:

| File | Type | Duration | Description |
|------|------|----------|-------------|
| F2BJRLP1 | Long-form | ~XX.X sec | News/speech content |
| F2BJRLP2 | Long-form | ~XX.X sec | News/speech content |
| F2BJRLP3 | Long-form | ~XX.X sec | News/speech content |
| ISLE_SESS0131_BLOCKD02_01 | Short utterance | ~X.X sec | Single sentence |
| ISLE_SESS0131_BLOCKD02_02 | Short utterance | ~X.X sec | Single sentence |
| ISLE_SESS0131_BLOCKD02_03 | Short utterance | ~X.X sec | Single sentence |

### 3.3 Data Preparation

**Steps taken:**
1. Validated audio file format (WAV, sample rate, channels)
2. Normalized transcript filenames to match audio files
3. Cleaned transcript text (removed extra whitespace, formatting)
4. Organized files in MFA-required structure:
   ```
   mfa_data/corpus/
   ├── file1.wav
   ├── file1.txt
   ├── file2.wav
   ├── file2.txt
   └── ...
   ```

**Text Cleaning:**
- Removed extra whitespace and line breaks
- Ensured consistent formatting
- Preserved original case and punctuation

### 3.4 Model Selection

**Pronunciation Dictionary:** `english_us_arpa`
- Contains phonetic transcriptions for common English words
- Uses ARPA phoneme set
- Pre-trained on large English corpus

**Acoustic Model:** `english_us_arpa`
- Trained on diverse English speech data
- Optimized for general American English
- Suitable for various speaking styles

### 3.5 Alignment Process

**Command used:**
```bash
mfa align mfa_data/corpus english_us_arpa english_us_arpa outputs/textgrids \
    --clean --beam 100 --retry_beam 400
```

**Parameters:**
- `--beam 100`: Beam width for acoustic model search
- `--retry_beam 400`: Increased beam for difficult segments
- `--clean`: Remove temporary files after completion

**Processing Time:** [X] minutes for [Y] files

---

## 4. Results

### 4.1 Alignment Statistics

**Overall Statistics:**
- Total files aligned: [X]
- Total audio duration: [XX.X] seconds ([X.X] minutes)
- Total words aligned: [XXX]
- Total phonemes aligned: [XXX]
- Average words per file: [XX]
- Average phonemes per file: [XXX]

**Duration Statistics:**

| Metric | Words | Phonemes |
|--------|-------|----------|
| Mean | X.XXX sec | X.XXX sec |
| Median | X.XXX sec | X.XXX sec |
| Std Dev | X.XXX sec | X.XXX sec |
| Min | X.XXX sec | X.XXX sec |
| Max | X.XXX sec | X.XXX sec |

### 4.2 Sample Alignment Visualization

**Example: [Filename]**

[Insert Praat screenshot here showing TextGrid with word and phone tiers]

**Observations:**
- Clear word boundaries visible at [timestamps]
- Phoneme segmentation shows [observation]
- Silence regions properly detected

**TextGrid Structure:**
- **Words Tier:** Contains word-level alignments
  - Example: "HELLO" at 0.00-0.45s
- **Phones Tier:** Contains phoneme-level alignments
  - Example: "HH" at 0.00-0.10s, "AH" at 0.10-0.25s, etc.

### 4.3 Visualizations

#### 4.3.1 Word Duration Distribution

[Insert word_duration_histogram.png here]

**Analysis:**
- Most words fall within [X-Y] second range
- Distribution shows [normal/skewed] pattern
- Outliers: [description of any unusual durations]

#### 4.3.2 Phoneme Duration Distribution

[Insert phoneme_duration_histogram.png here]

**Analysis:**
- Phoneme durations typically [X-Y] seconds
- Shorter than word durations as expected
- Consonants vs vowels show [pattern]

#### 4.3.3 Per-File Statistics

[Insert per_file_statistics.png here]

**Analysis:**
- Consistent alignment quality across files
- [Filename] has highest word count: [X] words
- [Filename] has shortest duration: [X] seconds

---

## 5. Analysis and Observations

### 5.1 Alignment Quality

**Positive Observations:**
1. ✓ All files successfully aligned
2. ✓ Word boundaries appear accurate upon inspection
3. ✓ Phoneme segmentation matches acoustic features
4. ✓ Silence regions properly identified

**Issues Identified:**
1. ⚠ [X] phonemes shorter than 20ms (may indicate alignment issues)
2. ⚠ [X] words longer than 2 seconds (compound words or misalignment)
3. ⚠ [List any OOV words if present]

### 5.2 Praat Inspection

**Manual Verification:**
- Opened TextGrid files in Praat
- Cross-referenced with audio waveform and spectrogram
- Verified timing accuracy of [X] sample words
- Checked phoneme boundaries against formant transitions

**Findings:**
- Word boundaries align well with acoustic pauses
- Phoneme boundaries generally match formant transitions
- Some phonemes may be slightly over/under-segmented
- Overall accuracy appears [good/excellent/acceptable]

### 5.3 Error Analysis

**Out-of-Vocabulary (OOV) Words:**
- Number of OOV words: [X]
- Examples: [list any OOV words]
- Impact: [description of how OOV affected alignment]

**Timing Offsets:**
- [Description of any systematic timing issues]
- [Possible causes: speech rate, audio quality, etc.]

**Problematic Segments:**
- Fast speech regions: [observations]
- Background noise: [impact if any]
- Overlapping speech: [if applicable]

---

## 6. Key Learnings

### 6.1 Technical Insights

1. **Data Preparation is Critical**
   - Proper file naming and organization essential
   - Text normalization affects alignment quality
   - Audio quality directly impacts results

2. **Model Selection Matters**
   - Dictionary coverage affects OOV rate
   - Acoustic model should match speaking style
   - Pre-trained models work well for standard speech

3. **Parameter Tuning**
   - Beam width affects accuracy vs speed tradeoff
   - Retry beam helps with difficult segments
   - Default parameters generally sufficient

### 6.2 Practical Applications

1. **Speech Research:** Enables precise timing measurements
2. **Corpus Creation:** Automates annotation of large datasets
3. **Speech Synthesis:** Training data for TTS systems
4. **Language Learning:** Pronunciation feedback systems
5. **Phonetics Studies:** Analyzing timing patterns

---

## 7. Challenges and Solutions

### 7.1 Challenges Encountered

1. **Challenge:** [Describe specific challenge]
   - **Solution:** [How you solved it]

2. **Challenge:** [Another challenge]
   - **Solution:** [Solution implemented]

### 7.2 Improvements for Future Work

1. Train custom pronunciation dictionary using G2P model
2. Compare multiple acoustic models (english_mfa, etc.)
3. Implement automated quality assessment
4. Handle OOV words more robustly
5. Fine-tune beam parameters per file

---

## 8. Conclusion

This project successfully implemented a complete forced alignment pipeline using the Montreal Forced Aligner. The system accurately aligned [X] audio files, generating [X] TextGrid files with precise word and phoneme boundaries.

**Key Achievements:**
- Automated pipeline from raw data to analyzed results
- High-quality alignments suitable for research use
- Comprehensive analysis and visualization tools
- Reproducible workflow documented

**Future Directions:**
- Expand to larger datasets
- Implement custom dictionary training
- Compare multiple alignment tools
- Develop automated quality metrics

The forced alignment process proved effective for synchronizing audio and text, with potential applications in speech research, corpus development, and language technology.

---

## 9. References

1. Montreal Forced Aligner Documentation: https://montreal-forced-aligner.readthedocs.io/
2. McAuliffe, M., Socolof, M., Mihuc, S., Wagner, M., & Sonderegger, M. (2017). Montreal Forced Aligner: Trainable Text-Speech Alignment Using Kaldi.
3. Praat: Doing Phonetics by Computer: https://www.praat.org/
4. ARPABET Phoneme Set: https://en.wikipedia.org/wiki/ARPABET

---

## 10. Appendix

### A. Command Reference

**Setup:**
```bash
conda create -n mfa python=3.10 -y
conda activate mfa
conda install -c conda-forge montreal-forced-aligner
```

**Data Preparation:**
```bash
python scripts/prepare_data.py
```

**Run Alignment:**
```bash
python scripts/run_alignment.py
```

**Analysis:**
```bash
python scripts/analyze_outputs.py
```

### B. File Structure

```
Assignment/
├── README.md
├── requirements.txt
├── wav/                    # Original audio files
├── transcripts/            # Original transcripts
├── mfa_data/corpus/        # Prepared corpus
├── outputs/
│   ├── textgrids/         # Generated TextGrid files
│   ├── logs/              # Alignment logs
│   ├── visualizations/    # Analysis plots
│   ├── analysis_report.json
│   └── analysis_report.txt
├── scripts/
│   ├── setup_mfa.py
│   ├── prepare_data.py
│   ├── run_alignment.py
│   ├── analyze_outputs.py
│   └── test_pipeline.py
└── docs/
    └── report.pdf
```

### C. GitHub Repository

Repository URL: [Your GitHub URL]

Contains:
- All source code and scripts
- Documentation and README
- Sample outputs (excluding large audio files)
- Setup instructions
- Analysis results

---

**End of Report**
