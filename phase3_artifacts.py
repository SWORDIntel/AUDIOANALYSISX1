"""
PHASE 3: ARTIFACT & COHERENCE ANALYSIS (AUGMENTED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Find the "smoking gun" for *both* pitch-shifting and time-stretching
"""

import librosa
import numpy as np
from scipy import stats


class ArtifactAnalyzer:
    """
    Multi-vector artifact detection for voice manipulation.
    Detects pitch-shifting and time-stretching artifacts.
    """

    def __init__(self):
        self.detection_results = {}

    def analyze(self, y, sr, phase1_results, phase2_results):
        """
        Comprehensive artifact analysis combining three detection methods.

        Args:
            y: Audio time series
            sr: Sample rate
            phase1_results: Results from baseline F0 analysis
            phase2_results: Results from vocal tract analysis

        Returns:
            dict: Comprehensive artifact analysis results
        """
        # PHASE 3.1: Pitch-Formant Incoherence
        incoherence = self._analyze_pitch_formant_incoherence(
            phase1_results, phase2_results
        )

        # PHASE 3.2: Mel Spectrogram Artifacts
        mel_artifacts = self._analyze_mel_spectrogram(y, sr)

        # PHASE 3.3: Phase/Transient Artifacts (Time-Stretch Detection)
        phase_artifacts = self._analyze_phase_coherence(y, sr)

        return {
            'pitch_formant_incoherence': incoherence,
            'mel_spectrogram_artifacts': mel_artifacts,
            'phase_artifacts': phase_artifacts,
            'overall_manipulation_detected': (
                incoherence['incoherence_detected'] or
                mel_artifacts['artifacts_detected'] or
                phase_artifacts['transient_smearing_detected']
            )
        }

    def _analyze_pitch_formant_incoherence(self, phase1_results, phase2_results):
        """
        PHASE 3.1: Detect pitch-shift manipulation by comparing F0 vs Formants.

        The key insight: Pitch-shifting changes F0 but cannot change formants
        (which are determined by physical vocal tract geometry).

        Args:
            phase1_results: Baseline F0 analysis
            phase2_results: Vocal tract formant analysis

        Returns:
            dict: Incoherence analysis results
        """
        presented_sex = phase1_results['presented_sex']
        probable_sex = phase2_results['probable_sex']

        # Direct contradiction is the smoking gun
        incoherence_detected = (presented_sex != probable_sex)

        # Calculate confidence score based on separation
        f0_median = phase1_results['f0_median']
        f1_median = phase2_results['f1_median']
        f2_median = phase2_results['f2_median']

        # Calculate how far the formants are from expected values for presented pitch
        if presented_sex == 'Female':
            # If presented as female, but formants are male-like
            expected_f1_range = (600, 1000)
            expected_f2_range = (1400, 2200)
        else:
            # If presented as male, but formants are female-like
            expected_f1_range = (400, 800)
            expected_f2_range = (1000, 1500)

        # Calculate deviation scores
        f1_deviation = 0
        if f1_median < expected_f1_range[0]:
            f1_deviation = (expected_f1_range[0] - f1_median) / expected_f1_range[0]
        elif f1_median > expected_f1_range[1]:
            f1_deviation = (f1_median - expected_f1_range[1]) / expected_f1_range[1]

        f2_deviation = 0
        if f2_median < expected_f2_range[0]:
            f2_deviation = (expected_f2_range[0] - f2_median) / expected_f2_range[0]
        elif f2_median > expected_f2_range[1]:
            f2_deviation = (f2_median - expected_f2_range[1]) / expected_f2_range[1]

        # Average deviation as confidence metric
        confidence = min(0.5 + (f1_deviation + f2_deviation) / 2, 0.99)

        return {
            'incoherence_detected': incoherence_detected,
            'presented_sex': presented_sex,
            'probable_sex': probable_sex,
            'confidence': float(confidence) if incoherence_detected else 0.0,
            'evidence': (
                f"Pitch suggests {presented_sex} (F0: {f0_median:.1f} Hz), "
                f"but formants suggest {probable_sex} "
                f"(F1: {f1_median:.1f} Hz, F2: {f2_median:.1f} Hz)"
            ) if incoherence_detected else "Pitch and formants are coherent"
        }

    def _analyze_mel_spectrogram(self, y, sr):
        """
        PHASE 3.2: Visual/statistical analysis of Mel spectrogram for artifacts.

        Looks for:
        - Unnatural "ringing" harmonics (pitch-shift artifacts)
        - Consistent computational noise floor
        - Spectral discontinuities

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            dict: Mel spectrogram artifact analysis
        """
        # Compute Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # Analyze noise floor consistency (artifact of processing)
        # Natural recordings have variable noise floor, processed audio has consistent floor
        noise_floor = np.percentile(mel_spec_db, 10, axis=1)
        noise_floor_std = np.std(noise_floor)

        # Lower std indicates more consistent (artificial) noise floor
        consistent_noise_floor = noise_floor_std < 3.0

        # Analyze spectral smoothness (ringing detection)
        # Calculate variation in spectral envelope
        spectral_envelope = np.mean(mel_spec_db, axis=1)
        spectral_gradient = np.gradient(spectral_envelope)
        spectral_smoothness = np.std(spectral_gradient)

        # High smoothness variance can indicate artificial harmonics
        unnatural_harmonics = spectral_smoothness > 2.5

        artifacts_detected = consistent_noise_floor or unnatural_harmonics

        return {
            'artifacts_detected': artifacts_detected,
            'consistent_noise_floor': consistent_noise_floor,
            'noise_floor_std': float(noise_floor_std),
            'unnatural_harmonics': unnatural_harmonics,
            'spectral_smoothness': float(spectral_smoothness),
            'mel_spectrogram': mel_spec_db,
            'evidence': self._generate_mel_evidence(
                consistent_noise_floor, unnatural_harmonics,
                noise_floor_std, spectral_smoothness
            )
        }

    def _generate_mel_evidence(self, noise_floor, harmonics, nf_std, smoothness):
        """Generate human-readable evidence string for mel analysis."""
        evidence = []
        if noise_floor:
            evidence.append(f"Consistent noise floor detected (std: {nf_std:.2f})")
        if harmonics:
            evidence.append(f"Unnatural harmonic structure (smoothness: {smoothness:.2f})")

        return "; ".join(evidence) if evidence else "No significant mel artifacts detected"

    def _analyze_phase_coherence(self, y, sr):
        """
        PHASE 3.3: Transient and Phase Artifact Analysis (Time-Stretch Detection).

        Time-stretching damages transients and creates phase discontinuities.
        This is the smoking gun for "sped up" audio.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            dict: Phase coherence analysis results
        """
        # Compute STFT
        D = librosa.stft(y, n_fft=2048, hop_length=512)

        # Extract magnitude and phase
        magnitude = np.abs(D)
        phase = np.angle(D)

        # Analyze phase coherence
        # In natural audio, phase changes smoothly
        # In time-stretched audio, phase has discontinuities
        phase_diff = np.diff(phase, axis=1)

        # Wrap phase differences to [-π, π]
        phase_diff = np.angle(np.exp(1j * phase_diff))

        # Calculate phase coherence metric
        # High variance in phase differences indicates manipulation
        phase_variance = np.var(phase_diff)

        # Calculate phase entropy (measure of disorder)
        # Time-stretched audio has higher entropy
        phase_entropy = stats.entropy(
            np.histogram(phase_diff.flatten(), bins=50)[0] + 1e-10
        )

        # Detect transient smearing
        # Calculate onset strength (transient detection)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        # Analyze onset sharpness
        # Time-stretching "smears" onsets (makes them less sharp)
        onset_sharpness = np.mean(np.abs(np.diff(onset_env)))

        # Low sharpness indicates smeared transients
        transient_smearing = onset_sharpness < 0.5

        # Overall detection
        # High phase variance OR low transient sharpness indicates time-stretching
        time_stretch_detected = (phase_variance > 2.5) or transient_smearing

        return {
            'transient_smearing_detected': time_stretch_detected,
            'phase_variance': float(phase_variance),
            'phase_entropy': float(phase_entropy),
            'onset_sharpness': float(onset_sharpness),
            'transient_smearing': transient_smearing,
            'phase_data': phase,
            'magnitude_data': magnitude,
            'evidence': self._generate_phase_evidence(
                time_stretch_detected, phase_variance,
                onset_sharpness, transient_smearing
            )
        }

    def _generate_phase_evidence(self, detected, variance, sharpness, smearing):
        """Generate human-readable evidence string for phase analysis."""
        if not detected:
            return "No phase artifacts detected - natural timing characteristics"

        evidence = []
        if variance > 2.5:
            evidence.append(f"High phase variance detected ({variance:.2f})")
        if smearing:
            evidence.append(f"Transient smearing detected (sharpness: {sharpness:.2f})")

        return "; ".join(evidence)
