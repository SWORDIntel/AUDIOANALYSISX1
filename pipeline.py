"""
VOICE MANIPULATION DETECTION PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Main orchestrator for the 5-phase forensic audio analysis system
"""

import librosa
import soundfile as sf
from pathlib import Path

from phase1_baseline import BaselineAnalyzer
from phase2_formants import VocalTractAnalyzer
from phase3_artifacts import ArtifactAnalyzer
from phase4_report import ReportSynthesizer
from phase5_ai_detection import AIVoiceDetector
from verification import OutputVerifier, ReportExporter


class VoiceManipulationDetector:
    """
    Main pipeline orchestrator for voice manipulation and AI voice detection.

    Executes 5-phase analysis:
    1. Baseline F0 Analysis
    2. Vocal Tract Formant Analysis
    3. Artifact & Coherence Analysis (Pitch-shift/Time-stretch)
    4. AI Voice Detection (Deepfake/TTS/Voice Cloning)
    5. Report Synthesis
    """

    def __init__(self):
        """Initialize all phase analyzers."""
        self.phase1 = BaselineAnalyzer()
        self.phase2 = VocalTractAnalyzer()
        self.phase3 = ArtifactAnalyzer()
        self.phase4 = AIVoiceDetector()
        self.phase5 = ReportSynthesizer()
        self.verifier = OutputVerifier()
        self.exporter = ReportExporter()

    def analyze(self, audio_path, output_dir=None, save_visualizations=True):
        """
        Execute complete forensic analysis pipeline.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            output_dir: Directory to save results (default: './results/')
            save_visualizations: Whether to save visualization plots

        Returns:
            dict: Comprehensive forensic report
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Setup output directory
        if output_dir is None:
            output_dir = Path('./results')
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        asset_id = audio_path.stem

        print(f"\n{'━' * 80}")
        print(f"INITIATING FORENSIC ANALYSIS: {asset_id}")
        print(f"{'━' * 80}\n")

        # Load audio
        print("[*] Loading audio file...")
        y, sr = librosa.load(str(audio_path), sr=None)
        print(f"    ✓ Loaded: {len(y)} samples @ {sr} Hz ({len(y)/sr:.2f} seconds)\n")

        # PHASE 1: Baseline F0 Analysis
        print("[PHASE 1] BASELINE ANALYSIS (ISOLATE THE DECEPTION)")
        print("━" * 80)
        print("[*] Extracting fundamental frequency (F0)...")
        phase1_results = self.phase1.analyze(y, sr)
        print(f"    ✓ F0 Median: {phase1_results['f0_median']:.1f} Hz")
        print(f"    ✓ Presented as: {phase1_results['presented_sex']}\n")

        # PHASE 2: Vocal Tract Analysis
        print("[PHASE 2] VOCAL TRACT ANALYSIS (BYPASS THE DECEPTION)")
        print("━" * 80)
        print("[*] Extracting formants (F1, F2, F3)...")
        phase2_results = self.phase2.analyze(str(audio_path), sr)
        print(f"    ✓ F1: {phase2_results['f1_median']:.0f} Hz")
        print(f"    ✓ F2: {phase2_results['f2_median']:.0f} Hz")
        print(f"    ✓ F3: {phase2_results['f3_median']:.0f} Hz")
        print(f"    ✓ Probable sex: {phase2_results['probable_sex']}\n")

        # PHASE 3: Artifact Analysis
        print("[PHASE 3] ARTIFACT & COHERENCE ANALYSIS (AUGMENTED)")
        print("━" * 80)
        print("[*] Analyzing pitch-formant coherence...")
        print("[*] Scanning mel spectrogram for artifacts...")
        print("[*] Detecting phase decoherence and transient smearing...")
        phase3_results = self.phase3.analyze(y, sr, phase1_results, phase2_results)

        if phase3_results['pitch_formant_incoherence']['incoherence_detected']:
            print("    ⚠ PITCH-FORMANT INCOHERENCE DETECTED")

        if phase3_results['mel_spectrogram_artifacts']['artifacts_detected']:
            print("    ⚠ SPECTRAL ARTIFACTS DETECTED")

        if phase3_results['phase_artifacts']['transient_smearing_detected']:
            print("    ⚠ TRANSIENT SMEARING / PHASE DECOHERENCE DETECTED")

        if not phase3_results['overall_manipulation_detected']:
            print("    ✓ No manipulation artifacts detected")

        print()

        # PHASE 4: AI Voice Detection
        print("[PHASE 4] AI VOICE DETECTION (DEEPFAKE/TTS/SYNTHETIC)")
        print("━" * 80)
        print("[*] Analyzing spectral artifacts (neural vocoder detection)...")
        print("[*] Analyzing prosody and naturalness...")
        print("[*] Detecting breathing patterns and pauses...")
        print("[*] Analyzing micro-timing consistency...")
        print("[*] Performing harmonic analysis...")
        print("[*] Extracting statistical features...")
        phase4_results = self.phase4.analyze(y, sr)

        if phase4_results['ai_detected']:
            print(f"    ⚠ AI VOICE DETECTED: {phase4_results['ai_type']}")
            print(f"    ⚠ Confidence: {phase4_results['confidence']:.0%}")
        else:
            print("    ✓ No AI voice artifacts detected")

        print()

        # PHASE 5: Report Synthesis
        print("[PHASE 5] SYNTHESIS & FINAL REPORT")
        print("━" * 80)
        print("[*] Synthesizing findings...")
        report = self.phase5.synthesize(
            asset_id, phase1_results, phase2_results, phase3_results, phase4_results
        )

        # Add verification metadata
        print("[*] Computing cryptographic verification...")
        report = self.verifier.sign_report(report, audio_path)

        # Save report (JSON)
        report_path = output_dir / f"{asset_id}_report.json"
        self.phase5.save_report(report, report_path)
        print(f"    ✓ Report saved: {report_path}")

        # Export Markdown version
        md_path = output_dir / f"{asset_id}_report.md"
        self.exporter.export_markdown(report, md_path)
        print(f"    ✓ Markdown report: {md_path}")

        # Generate visualizations
        if save_visualizations:
            from visualizer import Visualizer
            print("[*] Generating visualizations...")
            viz = Visualizer()
            viz_paths = viz.generate_all(
                audio_path, y, sr,
                phase1_results, phase2_results, phase3_results,
                output_dir, asset_id
            )
            print(f"    ✓ Visualizations saved: {len(viz_paths)} plots")

        # Print report
        self.phase5.print_report(report)

        return report

    def batch_analyze(self, audio_dir, output_dir=None, pattern='*.wav'):
        """
        Analyze multiple audio files in a directory.

        Args:
            audio_dir: Directory containing audio files
            output_dir: Directory to save results
            pattern: Glob pattern for audio files (default: '*.wav')

        Returns:
            list: List of reports for all analyzed files
        """
        audio_dir = Path(audio_dir)
        audio_files = list(audio_dir.glob(pattern))

        if not audio_files:
            print(f"No audio files found matching pattern: {pattern}")
            return []

        print(f"\n{'━' * 80}")
        print(f"BATCH ANALYSIS: {len(audio_files)} files found")
        print(f"{'━' * 80}\n")

        reports = []
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file.name}")
            try:
                report = self.analyze(audio_file, output_dir)
                reports.append(report)
            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue

        print(f"\n{'━' * 80}")
        print(f"BATCH ANALYSIS COMPLETE: {len(reports)}/{len(audio_files)} successful")
        print(f"{'━' * 80}\n")

        return reports


def main():
    """Example usage of the pipeline."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <audio_file>")
        print("   or: python pipeline.py <audio_directory> --batch")
        sys.exit(1)

    path = sys.argv[1]
    detector = VoiceManipulationDetector()

    if '--batch' in sys.argv:
        # Batch mode
        detector.batch_analyze(path)
    else:
        # Single file mode
        detector.analyze(path)


if __name__ == '__main__':
    main()
