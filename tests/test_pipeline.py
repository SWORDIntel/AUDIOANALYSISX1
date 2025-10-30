"""
COMPREHENSIVE TEST SUITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests all phases of the Voice Manipulation Detection Pipeline
"""

import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
import json
import sys

from pipeline import VoiceManipulationDetector
from verification import OutputVerifier


class TestSuiteRunner:
    """Comprehensive test suite for the pipeline."""

    def __init__(self):
        self.test_dir = Path('./test_audio')
        self.results_dir = Path('./test_results')
        self.detector = VoiceManipulationDetector()
        self.verifier = OutputVerifier()

        # Create directories
        self.test_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

    def generate_synthetic_male_voice(self, duration=3.0, sr=22050):
        """Generate synthetic male voice sample."""
        t = np.linspace(0, duration, int(sr * duration))

        # Male fundamental frequency (~120 Hz)
        f0 = 120
        y = np.sin(2 * np.pi * f0 * t) * 0.3

        # Add harmonics (typical of male voice)
        y += np.sin(2 * np.pi * f0 * 2 * t) * 0.2  # 2nd harmonic
        y += np.sin(2 * np.pi * f0 * 3 * t) * 0.1  # 3rd harmonic
        y += np.sin(2 * np.pi * f0 * 4 * t) * 0.05  # 4th harmonic

        # Add formant-like filtering (simulate male vocal tract)
        # This is a simplified approximation
        from scipy import signal
        # F1 (~500 Hz) resonance
        b, a = signal.butter(4, [450, 550], btype='band', fs=sr)
        y_f1 = signal.filtfilt(b, a, y) * 0.3

        # F2 (~1500 Hz) resonance
        b, a = signal.butter(4, [1400, 1600], btype='band', fs=sr)
        y_f2 = signal.filtfilt(b, a, y) * 0.2

        y = y + y_f1 + y_f2

        # Add noise
        y += np.random.normal(0, 0.02, len(y))

        # Normalize
        y = y / np.max(np.abs(y)) * 0.8

        return y, sr

    def generate_synthetic_female_voice(self, duration=3.0, sr=22050):
        """Generate synthetic female voice sample."""
        t = np.linspace(0, duration, int(sr * duration))

        # Female fundamental frequency (~220 Hz)
        f0 = 220
        y = np.sin(2 * np.pi * f0 * t) * 0.3

        # Add harmonics
        y += np.sin(2 * np.pi * f0 * 2 * t) * 0.2
        y += np.sin(2 * np.pi * f0 * 3 * t) * 0.1
        y += np.sin(2 * np.pi * f0 * 4 * t) * 0.05

        # Add formant-like filtering (simulate female vocal tract)
        from scipy import signal
        # F1 (~550 Hz) resonance
        b, a = signal.butter(4, [500, 600], btype='band', fs=sr)
        y_f1 = signal.filtfilt(b, a, y) * 0.3

        # F2 (~1650 Hz) resonance
        b, a = signal.butter(4, [1550, 1750], btype='band', fs=sr)
        y_f2 = signal.filtfilt(b, a, y) * 0.2

        y = y + y_f1 + y_f2

        # Add noise
        y += np.random.normal(0, 0.02, len(y))

        # Normalize
        y = y / np.max(np.abs(y)) * 0.8

        return y, sr

    def create_test_samples(self):
        """Create all test samples."""
        print("\n[TEST SUITE] Creating test audio samples...")
        print("━" * 80)

        # 1. Clean male voice
        print("  [1/6] Generating clean male voice...")
        y_male, sr = self.generate_synthetic_male_voice()
        male_path = self.test_dir / 'male_clean.wav'
        sf.write(male_path, y_male, sr)
        print(f"        ✓ Saved: {male_path}")

        # 2. Clean female voice
        print("  [2/6] Generating clean female voice...")
        y_female, sr = self.generate_synthetic_female_voice()
        female_path = self.test_dir / 'female_clean.wav'
        sf.write(female_path, y_female, sr)
        print(f"        ✓ Saved: {female_path}")

        # 3. Male voice pitch-shifted to female range
        print("  [3/6] Creating male voice pitched up (simulated manipulation)...")
        y_male_pitched = librosa.effects.pitch_shift(y_male, sr=sr, n_steps=6)
        male_pitched_path = self.test_dir / 'male_pitched_to_female.wav'
        sf.write(male_pitched_path, y_male_pitched, sr)
        print(f"        ✓ Saved: {male_pitched_path}")

        # 4. Female voice pitch-shifted to male range
        print("  [4/6] Creating female voice pitched down (simulated manipulation)...")
        y_female_pitched = librosa.effects.pitch_shift(y_female, sr=sr, n_steps=-6)
        female_pitched_path = self.test_dir / 'female_pitched_to_male.wav'
        sf.write(female_pitched_path, y_female_pitched, sr)
        print(f"        ✓ Saved: {female_pitched_path}")

        # 5. Male voice pitch-shifted AND time-stretched
        print("  [5/6] Creating male voice with pitch+time manipulation...")
        y_male_both = librosa.effects.time_stretch(y_male_pitched, rate=1.1)
        male_both_path = self.test_dir / 'male_pitch_time_manipulated.wav'
        sf.write(male_both_path, y_male_both, sr)
        print(f"        ✓ Saved: {male_both_path}")

        # 6. Female voice time-stretched only
        print("  [6/6] Creating female voice with time-stretch manipulation...")
        y_female_time = librosa.effects.time_stretch(y_female, rate=1.15)
        female_time_path = self.test_dir / 'female_time_stretched.wav'
        sf.write(female_time_path, y_female_time, sr)
        print(f"        ✓ Saved: {female_time_path}")

        print("\n✓ Test samples created successfully!\n")

        return [
            (male_path, False, "Clean male voice"),
            (female_path, False, "Clean female voice"),
            (male_pitched_path, True, "Male voice pitch-shifted"),
            (female_pitched_path, True, "Female voice pitch-shifted"),
            (male_both_path, True, "Male voice pitch+time manipulated"),
            (female_time_path, True, "Female voice time-stretched")
        ]

    def run_tests(self):
        """Run all tests."""
        print("\n" + "=" * 80)
        print("VOICE MANIPULATION DETECTION - COMPREHENSIVE TEST SUITE")
        print("=" * 80 + "\n")

        # Create test samples
        test_cases = self.create_test_samples()

        # Run analysis on each sample
        print("[TEST SUITE] Running analysis on all samples...")
        print("━" * 80 + "\n")

        results = []

        for i, (audio_path, expected_manipulation, description) in enumerate(test_cases, 1):
            print(f"[TEST {i}/{len(test_cases)}] {description}")
            print(f"  File: {audio_path.name}")
            print(f"  Expected: {'MANIPULATION' if expected_manipulation else 'CLEAN'}")

            try:
                # Run analysis
                report = self.detector.analyze(
                    audio_path,
                    output_dir=self.results_dir / audio_path.stem,
                    save_visualizations=True
                )

                # Verify detection
                detected = report['ALTERATION_DETECTED']
                correct = (detected == expected_manipulation)

                print(f"  Actual: {'MANIPULATION' if detected else 'CLEAN'}")
                print(f"  Confidence: {report['CONFIDENCE']}")
                print(f"  Result: {'✓ PASS' if correct else '✗ FAIL'}")

                results.append({
                    'test': description,
                    'expected': expected_manipulation,
                    'detected': detected,
                    'correct': correct,
                    'confidence': report['CONFIDENCE']
                })

            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results.append({
                    'test': description,
                    'expected': expected_manipulation,
                    'detected': None,
                    'correct': False,
                    'confidence': 'N/A',
                    'error': str(e)
                })

            print()

        # Print summary
        self.print_test_summary(results)

        # Test verification system
        self.test_verification_system()

        return results

    def print_test_summary(self, results):
        """Print test results summary."""
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80 + "\n")

        total = len(results)
        passed = sum(1 for r in results if r['correct'])
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({'✓' if passed == total else '⚠'})")
        print(f"Failed: {failed} ({'✓' if failed == 0 else '✗'})")
        print(f"Success Rate: {passed/total*100:.1f}%")

        print("\n" + "-" * 80)
        print("DETAILED RESULTS:")
        print("-" * 80 + "\n")

        for i, result in enumerate(results, 1):
            status = "✓ PASS" if result['correct'] else "✗ FAIL"
            print(f"{i}. {result['test']}")
            print(f"   Expected: {'MANIPULATION' if result['expected'] else 'CLEAN'}")
            print(f"   Detected: {'MANIPULATION' if result['detected'] else 'CLEAN'}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Status: {status}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            print()

    def test_verification_system(self):
        """Test the cryptographic verification system."""
        print("\n" + "=" * 80)
        print("VERIFICATION SYSTEM TEST")
        print("=" * 80 + "\n")

        # Find a report to test
        report_files = list(self.results_dir.glob('**/*_report.json'))

        if not report_files:
            print("⚠ No reports found to test verification")
            return

        test_report = report_files[0]
        print(f"Testing verification on: {test_report.name}")

        # Test 1: Verify intact report
        print("\n[TEST 1] Verifying intact report...")
        result = self.verifier.verify_report(test_report)

        if result['valid']:
            print("  ✓ PASS - Report verification successful")
            print(f"    Timestamp: {result['timestamp']}")
            print(f"    Audio File: {result['audio_file']}")
        else:
            print(f"  ✗ FAIL - {result['error']}")

        # Test 2: Detect tampered report
        print("\n[TEST 2] Detecting tampered report...")

        # Create a tampered copy
        with open(test_report, 'r') as f:
            report_data = json.load(f)

        # Tamper with the data
        original_confidence = report_data['CONFIDENCE']
        report_data['CONFIDENCE'] = 'TAMPERED'

        tampered_path = self.results_dir / 'tampered_report.json'
        with open(tampered_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        result = self.verifier.verify_report(tampered_path)

        if not result['valid'] and 'tampered' in result['error'].lower():
            print("  ✓ PASS - Tampering detected successfully")
            print(f"    Error: {result['error']}")
        else:
            print("  ✗ FAIL - Tampering not detected")

        # Clean up
        tampered_path.unlink()

        print("\n✓ Verification system tests complete!\n")


def main():
    """Run the test suite."""
    runner = TestSuiteRunner()
    results = runner.run_tests()

    # Exit with appropriate code
    all_passed = all(r['correct'] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
