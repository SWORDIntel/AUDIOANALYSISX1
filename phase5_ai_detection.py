"""
PHASE 5: AI VOICE DETECTION (DEEPFAKE & SYNTHETIC VOICE DETECTION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Detect AI-generated voices from TTS, voice cloning, and deepfakes
"""

import librosa
import numpy as np
from scipy import stats, signal
from scipy.fft import fft


class AIVoiceDetector:
    """
    Detects AI-generated voices using multiple neural vocoder artifact detection methods.

    Targets:
    - Neural TTS (Tacotron, FastSpeech, VITS)
    - Neural Vocoders (WaveNet, WaveGlow, HiFi-GAN)
    - Voice Cloning (Real-Time Voice Cloning, SV2TTS)
    - Deepfakes (FaceSwap audio, DeepFaceLab)
    """

    def __init__(self):
        self.detection_methods = []

    def analyze(self, y, sr):
        """
        Comprehensive AI voice detection analysis.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            dict: AI detection results
        """
        results = {
            'spectral_artifacts': self._detect_spectral_artifacts(y, sr),
            'prosody_analysis': self._analyze_prosody(y, sr),
            'breathing_pauses': self._detect_breathing_pauses(y, sr),
            'micro_timing': self._analyze_micro_timing(y, sr),
            'harmonic_analysis': self._analyze_harmonics(y, sr),
            'statistical_features': self._extract_statistical_features(y, sr)
        }

        # Overall AI detection
        results['ai_detected'] = self._compute_ai_detection(results)
        results['confidence'] = self._compute_ai_confidence(results)
        results['ai_type'] = self._classify_ai_type(results)

        return results

    def _detect_spectral_artifacts(self, y, sr):
        """
        Detect spectral artifacts specific to neural vocoders.

        Neural vocoders (WaveNet, WaveGlow, HiFi-GAN) produce characteristic
        artifacts in the high-frequency range and phase spectrum.
        """
        # Compute high-resolution spectrogram
        D = librosa.stft(y, n_fft=4096, hop_length=512)
        magnitude = np.abs(D)
        magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)

        # 1. High-frequency artifacts (neural vocoders struggle above 8kHz)
        nyquist = sr / 2
        high_freq_start = int(8000 / nyquist * magnitude.shape[0])
        high_freq_energy = np.mean(magnitude_db[high_freq_start:, :])
        low_freq_energy = np.mean(magnitude_db[:high_freq_start, :])

        # AI voices often have unnaturally low high-frequency content
        freq_ratio = high_freq_energy / (low_freq_energy + 1e-10)
        unnatural_freq_distribution = freq_ratio < -40  # dB ratio

        # 2. Spectral rolloff consistency
        # AI voices have very consistent rolloff, human voices vary
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        rolloff_std = np.std(rolloff)
        rolloff_too_consistent = rolloff_std < 500  # Hz

        # 3. Spectral flux (rate of change in spectrum)
        # AI voices have unnatural spectral stability
        spectral_flux = np.sqrt(np.mean(np.diff(magnitude, axis=1)**2, axis=0))
        flux_mean = np.mean(spectral_flux)
        flux_std = np.std(spectral_flux)
        flux_too_stable = flux_std / (flux_mean + 1e-10) < 0.3

        # 4. Phase discontinuities (vocoder artifacts)
        phase = np.angle(D)
        phase_diff = np.diff(phase, axis=1)
        phase_jumps = np.sum(np.abs(phase_diff) > np.pi * 0.9) / phase_diff.size
        excessive_phase_jumps = phase_jumps > 0.15

        return {
            'unnatural_freq_distribution': unnatural_freq_distribution,
            'rolloff_too_consistent': rolloff_too_consistent,
            'flux_too_stable': flux_too_stable,
            'excessive_phase_jumps': excessive_phase_jumps,
            'freq_ratio_db': float(freq_ratio),
            'rolloff_std': float(rolloff_std),
            'flux_stability': float(flux_std / (flux_mean + 1e-10)),
            'phase_jump_ratio': float(phase_jumps),
            'artifacts_detected': any([
                unnatural_freq_distribution,
                rolloff_too_consistent,
                flux_too_stable,
                excessive_phase_jumps
            ])
        }

    def _analyze_prosody(self, y, sr):
        """
        Analyze prosody patterns for unnatural characteristics.

        AI voices often have:
        - Overly smooth pitch contours
        - Unnatural energy distribution
        - Lack of micro-variations
        """
        # Extract pitch contour
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=400)
        pitch_contour = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_contour.append(pitch)

        pitch_contour = np.array(pitch_contour)

        if len(pitch_contour) < 10:
            return {
                'unnatural_pitch_smoothness': False,
                'lack_of_variation': False,
                'pitch_contour_score': 0.0,
                'prosody_artifacts': False
            }

        # 1. Pitch smoothness (AI is too smooth)
        pitch_diff = np.diff(pitch_contour)
        pitch_smoothness = np.std(pitch_diff)
        too_smooth = pitch_smoothness < 2.0  # Hz/frame

        # 2. Lack of micro-variations
        # Real voices have small random variations, AI is deterministic
        pitch_detrended = pitch_contour - signal.savgol_filter(pitch_contour, 11, 2)
        micro_variation = np.std(pitch_detrended)
        lacks_variation = micro_variation < 1.0  # Hz

        # 3. Energy contour analysis
        rms = librosa.feature.rms(y=y)[0]
        energy_smoothness = np.std(np.diff(rms))
        energy_too_smooth = energy_smoothness < 0.005

        # 4. Pitch-energy correlation (AI often has unnatural correlation)
        if len(pitch_contour) == len(rms):
            correlation = np.corrcoef(pitch_contour, rms)[0, 1]
            unnatural_correlation = abs(correlation) > 0.8
        else:
            unnatural_correlation = False

        prosody_score = sum([too_smooth, lacks_variation, energy_too_smooth, unnatural_correlation]) / 4.0

        return {
            'unnatural_pitch_smoothness': too_smooth,
            'lack_of_variation': lacks_variation,
            'energy_too_smooth': energy_too_smooth,
            'unnatural_correlation': unnatural_correlation,
            'pitch_smoothness': float(pitch_smoothness),
            'micro_variation': float(micro_variation),
            'prosody_score': float(prosody_score),
            'prosody_artifacts': prosody_score > 0.5
        }

    def _detect_breathing_pauses(self, y, sr):
        """
        Detect presence of natural breathing and pauses.

        AI voices often lack:
        - Breath sounds
        - Natural pauses
        - Irregular timing
        """
        # Detect silence regions
        intervals = librosa.effects.split(y, top_db=30)

        if len(intervals) < 2:
            return {
                'lacks_natural_pauses': True,
                'no_breathing_detected': True,
                'pause_count': 0,
                'breathing_artifacts': True
            }

        # Calculate pause durations
        pause_durations = []
        for i in range(len(intervals) - 1):
            pause_start = intervals[i][1]
            pause_end = intervals[i + 1][0]
            pause_duration = (pause_end - pause_start) / sr
            if pause_duration > 0.05:  # Minimum 50ms
                pause_durations.append(pause_duration)

        # 1. Check for natural pause distribution
        if len(pause_durations) > 0:
            pause_std = np.std(pause_durations)
            lacks_natural_pauses = pause_std < 0.05  # Too consistent
        else:
            lacks_natural_pauses = True

        # 2. Detect breath sounds (low-frequency, low-energy noise)
        # Extract low-frequency components
        y_low = librosa.effects.preemphasis(y, coef=-0.97)  # Emphasize low freq

        # Look for breath-like sounds (broadband, low-energy)
        breath_detected = False
        for i in range(len(intervals) - 1):
            pause_start = intervals[i][1]
            pause_end = intervals[i + 1][0]
            if pause_end - pause_start > sr * 0.1:  # At least 100ms pause
                pause_segment = y_low[pause_start:pause_end]
                if len(pause_segment) > 0:
                    # Breath sounds have specific spectral characteristics
                    breath_energy = np.mean(np.abs(pause_segment))
                    if 0.001 < breath_energy < 0.05:  # Weak but present
                        breath_detected = True
                        break

        no_breathing = not breath_detected

        return {
            'lacks_natural_pauses': lacks_natural_pauses,
            'no_breathing_detected': no_breathing,
            'pause_count': len(pause_durations),
            'avg_pause_duration': float(np.mean(pause_durations)) if pause_durations else 0.0,
            'pause_std': float(np.std(pause_durations)) if pause_durations else 0.0,
            'breathing_artifacts': lacks_natural_pauses or no_breathing
        }

    def _analyze_micro_timing(self, y, sr):
        """
        Analyze micro-timing consistency.

        AI voices are often TOO perfect in timing, lacking natural jitter.
        """
        # Detect onsets (note starts)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 5:
            return {
                'timing_too_perfect': False,
                'lacks_jitter': False,
                'onset_count': len(onsets),
                'timing_artifacts': False
            }

        # Calculate inter-onset intervals (IOI)
        ioi = np.diff(onsets)

        # 1. Check for unnatural consistency
        ioi_cv = np.std(ioi) / (np.mean(ioi) + 1e-10)  # Coefficient of variation
        timing_too_perfect = ioi_cv < 0.15  # Too little variation

        # 2. Check for jitter in timing
        # Real speakers have micro-variations, AI is deterministic
        if len(ioi) > 3:
            ioi_detrended = ioi - signal.savgol_filter(ioi, min(len(ioi), 5), 1)
            jitter = np.std(ioi_detrended)
            lacks_jitter = jitter < 0.01  # seconds
        else:
            lacks_jitter = False

        return {
            'timing_too_perfect': timing_too_perfect,
            'lacks_jitter': lacks_jitter,
            'onset_count': len(onsets),
            'ioi_cv': float(ioi_cv),
            'jitter': float(jitter) if len(ioi) > 3 else 0.0,
            'timing_artifacts': timing_too_perfect or lacks_jitter
        }

    def _analyze_harmonics(self, y, sr):
        """
        Analyze harmonic structure for AI artifacts.

        Neural vocoders often produce:
        - Unnatural harmonic-to-noise ratio
        - Too-perfect harmonic alignment
        - Missing or exaggerated harmonics
        """
        # Compute harmonic and percussive components
        y_harmonic, y_percussive = librosa.effects.hpss(y)

        # 1. Harmonic-to-Noise Ratio (HNR)
        harmonic_energy = np.sum(y_harmonic ** 2)
        noise_energy = np.sum(y_percussive ** 2)
        hnr = 10 * np.log10((harmonic_energy + 1e-10) / (noise_energy + 1e-10))

        # AI voices often have unnaturally high HNR
        hnr_too_high = hnr > 25  # dB

        # 2. Harmonic alignment consistency
        # Extract fundamental and harmonics
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        f0_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            if magnitudes[index, t] > 0:
                f0_values.append(pitches[index, t])

        if len(f0_values) > 10:
            f0_std = np.std(f0_values)
            harmonics_too_perfect = f0_std < 1.0  # Hz
        else:
            harmonics_too_perfect = False

        # 3. Spectral centroid consistency
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        centroid_cv = np.std(spectral_centroid) / (np.mean(spectral_centroid) + 1e-10)
        centroid_too_stable = centroid_cv < 0.1

        return {
            'hnr_too_high': hnr_too_high,
            'harmonics_too_perfect': harmonics_too_perfect,
            'centroid_too_stable': centroid_too_stable,
            'hnr_db': float(hnr),
            'harmonic_artifacts': any([hnr_too_high, harmonics_too_perfect, centroid_too_stable])
        }

    def _extract_statistical_features(self, y, sr):
        """
        Extract statistical features for AI detection.

        Uses MFCC and other features to detect statistical anomalies.
        """
        # Extract MFCCs (Mel-Frequency Cepstral Coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

        # Calculate statistical moments
        mfcc_means = np.mean(mfccs, axis=1)
        mfcc_stds = np.std(mfccs, axis=1)
        mfcc_skewness = stats.skew(mfccs, axis=1)
        mfcc_kurtosis = stats.kurtosis(mfccs, axis=1)

        # AI voices often have:
        # 1. Lower variance in MFCCs
        low_variance = np.mean(mfcc_stds) < 15.0

        # 2. Abnormal distribution (skewness/kurtosis)
        abnormal_distribution = (
            np.mean(np.abs(mfcc_skewness)) > 1.5 or
            np.mean(np.abs(mfcc_kurtosis)) > 4.0
        )

        # 3. Zero-crossing rate consistency
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        zcr_std = np.std(zcr)
        zcr_too_consistent = zcr_std < 0.02

        return {
            'low_variance': low_variance,
            'abnormal_distribution': abnormal_distribution,
            'zcr_too_consistent': zcr_too_consistent,
            'mfcc_mean_std': float(np.mean(mfcc_stds)),
            'statistical_artifacts': any([low_variance, abnormal_distribution, zcr_too_consistent])
        }

    def _compute_ai_detection(self, results):
        """
        Compute overall AI detection based on all methods.

        Returns True if AI voice is detected.
        """
        detections = [
            results['spectral_artifacts']['artifacts_detected'],
            results['prosody_analysis']['prosody_artifacts'],
            results['breathing_pauses']['breathing_artifacts'],
            results['micro_timing']['timing_artifacts'],
            results['harmonic_analysis']['harmonic_artifacts'],
            results['statistical_features']['statistical_artifacts']
        ]

        # AI detected if 3+ methods trigger
        return sum(detections) >= 3

    def _compute_ai_confidence(self, results):
        """
        Compute confidence score for AI detection (0.0 to 1.0).
        """
        detections = [
            results['spectral_artifacts']['artifacts_detected'],
            results['prosody_analysis']['prosody_artifacts'],
            results['breathing_pauses']['breathing_artifacts'],
            results['micro_timing']['timing_artifacts'],
            results['harmonic_analysis']['harmonic_artifacts'],
            results['statistical_features']['statistical_artifacts']
        ]

        detection_count = sum(detections)

        if detection_count == 0:
            return 0.0
        elif detection_count == 1:
            return 0.3
        elif detection_count == 2:
            return 0.6
        elif detection_count == 3:
            return 0.8
        elif detection_count == 4:
            return 0.9
        else:  # 5 or 6
            return 0.95

    def _classify_ai_type(self, results):
        """
        Attempt to classify the type of AI voice synthesis.

        Returns:
            str: AI type classification or 'Unknown'
        """
        if not results['ai_detected']:
            return 'None (Human Voice)'

        # Analyze pattern of detections
        spectral = results['spectral_artifacts']['artifacts_detected']
        prosody = results['prosody_analysis']['prosody_artifacts']
        breathing = results['breathing_pauses']['breathing_artifacts']
        timing = results['micro_timing']['timing_artifacts']
        harmonic = results['harmonic_analysis']['harmonic_artifacts']

        # Pattern matching for common AI voice types
        if spectral and harmonic and breathing:
            return 'Neural Vocoder (WaveNet/WaveGlow/HiFi-GAN)'
        elif prosody and timing and breathing:
            return 'TTS System (Tacotron/FastSpeech)'
        elif spectral and prosody and not breathing:
            return 'Voice Cloning (Real-Time VC)'
        elif all([spectral, prosody, breathing, timing]):
            return 'Advanced Deepfake (Multi-stage synthesis)'
        else:
            return 'AI-Generated (Type Unknown)'
