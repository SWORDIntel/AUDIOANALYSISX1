"""
EXAMPLE USAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Demonstrates how to use the Voice Manipulation Detection Pipeline
"""

from pipeline import VoiceManipulationDetector
from pathlib import Path


def example_single_file():
    """Example: Analyze a single audio file."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Single File Analysis")
    print("=" * 80 + "\n")

    detector = VoiceManipulationDetector()

    # Replace with your audio file path
    audio_file = "sample_audio.wav"

    if not Path(audio_file).exists():
        print(f"Error: Audio file not found: {audio_file}")
        print("Please provide a valid audio file path.")
        return

    # Analyze
    report = detector.analyze(
        audio_path=audio_file,
        output_dir='./results',
        save_visualizations=True
    )

    # Access specific results
    print("\nKey Findings:")
    print(f"  Alteration Detected: {report['ALTERATION_DETECTED']}")
    print(f"  Confidence: {report['CONFIDENCE']}")
    print(f"  Presented As: {report['PRESENTED_AS']}")
    print(f"  Probable Sex: {report['PROBABLE_SEX']}")


def example_batch_analysis():
    """Example: Analyze multiple audio files in a directory."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Batch Analysis")
    print("=" * 80 + "\n")

    detector = VoiceManipulationDetector()

    # Replace with your audio directory
    audio_directory = "./audio_samples"

    if not Path(audio_directory).exists():
        print(f"Error: Directory not found: {audio_directory}")
        print("Please provide a valid directory path.")
        return

    # Analyze all WAV files in directory
    reports = detector.batch_analyze(
        audio_dir=audio_directory,
        output_dir='./batch_results',
        pattern='*.wav'  # Can also use '*.mp3', '*.flac', etc.
    )

    # Summary statistics
    manipulated_count = sum(1 for r in reports if r['ALTERATION_DETECTED'])

    print("\nBatch Analysis Summary:")
    print(f"  Total Files: {len(reports)}")
    print(f"  Manipulated: {manipulated_count}")
    print(f"  Authentic: {len(reports) - manipulated_count}")


def example_create_test_sample():
    """Example: Create a manipulated test sample for demonstration."""
    import librosa
    import soundfile as sf
    import numpy as np

    print("\n" + "=" * 80)
    print("EXAMPLE 3: Create Test Sample with Known Manipulation")
    print("=" * 80 + "\n")

    # Load a sample audio file
    source_file = "original.wav"

    if not Path(source_file).exists():
        print(f"Error: Source file not found: {source_file}")
        print("Generating synthetic test audio instead...")

        # Generate synthetic male voice (low pitch)
        duration = 3.0
        sr = 22050
        t = np.linspace(0, duration, int(sr * duration))

        # Male fundamental frequency (~120 Hz) with harmonics
        f0 = 120
        y = np.sin(2 * np.pi * f0 * t) * 0.3
        y += np.sin(2 * np.pi * f0 * 2 * t) * 0.2  # Second harmonic
        y += np.sin(2 * np.pi * f0 * 3 * t) * 0.1  # Third harmonic

        # Add some noise
        y += np.random.normal(0, 0.05, len(y))

        # Save original
        sf.write('test_male_original.wav', y, sr)
        print("✓ Generated synthetic male voice: test_male_original.wav")

        source_file = 'test_male_original.wav'

    # Load the source
    y, sr = librosa.load(source_file, sr=None)

    # Apply manipulations (simulate what an adversary might do)
    print("\nApplying manipulations:")

    # 1. Pitch shift up by 6 semitones (male -> female range)
    print("  [1] Pitch shifting +6 semitones...")
    y_pitched = librosa.effects.pitch_shift(y, sr=sr, n_steps=6)

    # 2. Speed up by 10%
    print("  [2] Time stretching (speeding up by 10%)...")
    y_manipulated = librosa.effects.time_stretch(y_pitched, rate=1.1)

    # Save manipulated version
    output_file = 'test_manipulated.wav'
    sf.write(output_file, y_manipulated, sr)
    print(f"\n✓ Saved manipulated audio: {output_file}")

    # Now analyze it
    print("\nAnalyzing manipulated sample...")
    detector = VoiceManipulationDetector()
    report = detector.analyze(output_file, output_dir='./test_results')

    print("\nExpected: MANIPULATION DETECTED")
    print(f"Actual: {'MANIPULATION DETECTED' if report['ALTERATION_DETECTED'] else 'NO MANIPULATION'}")
    print(f"Confidence: {report['CONFIDENCE']}")


def example_programmatic_access():
    """Example: Access detailed analysis results programmatically."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Programmatic Access to Results")
    print("=" * 80 + "\n")

    detector = VoiceManipulationDetector()

    audio_file = "sample_audio.wav"
    if not Path(audio_file).exists():
        print(f"Error: Audio file not found: {audio_file}")
        return

    report = detector.analyze(audio_file, save_visualizations=False)

    # Access detailed findings
    findings = report['DETAILED_FINDINGS']

    print("Detailed Phase Results:")
    print("\n[PHASE 1] Baseline F0 Analysis:")
    print(f"  F0 Median: {findings['phase1_baseline']['f0_median']:.2f} Hz")
    print(f"  F0 Mean: {findings['phase1_baseline']['f0_mean']:.2f} Hz")
    print(f"  F0 Std Dev: {findings['phase1_baseline']['f0_std']:.2f} Hz")

    print("\n[PHASE 2] Formant Analysis:")
    print(f"  F1: {findings['phase2_formants']['f1_median']:.0f} Hz")
    print(f"  F2: {findings['phase2_formants']['f2_median']:.0f} Hz")
    print(f"  F3: {findings['phase2_formants']['f3_median']:.0f} Hz")

    print("\n[PHASE 3] Artifact Detection:")
    artifacts = findings['phase3_artifacts']

    print("  Pitch-Formant Incoherence:")
    print(f"    Detected: {artifacts['pitch_formant_incoherence']['detected']}")
    print(f"    Confidence: {artifacts['pitch_formant_incoherence']['confidence']:.2%}")

    print("  Mel Spectrogram Analysis:")
    print(f"    Artifacts: {artifacts['mel_spectrogram']['artifacts_detected']}")
    print(f"    Noise Floor: {artifacts['mel_spectrogram']['consistent_noise_floor']}")

    print("  Phase Coherence Analysis:")
    print(f"    Time-Stretch Detected: {artifacts['phase_coherence']['time_stretch_detected']}")
    print(f"    Phase Variance: {artifacts['phase_coherence']['phase_variance']:.2f}")


if __name__ == '__main__':
    import sys

    examples = {
        '1': example_single_file,
        '2': example_batch_analysis,
        '3': example_create_test_sample,
        '4': example_programmatic_access
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("\nVoice Manipulation Detection Pipeline - Examples")
        print("=" * 80)
        print("\nUsage: python example.py <example_number>")
        print("\nAvailable Examples:")
        print("  1 - Single File Analysis")
        print("  2 - Batch Analysis")
        print("  3 - Create Test Sample with Known Manipulation")
        print("  4 - Programmatic Access to Results")
        print("\nExample: python example.py 3")
        print("=" * 80 + "\n")
