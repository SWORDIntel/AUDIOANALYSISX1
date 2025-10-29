"""
VISUALIZATION UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate visualization plots for forensic audio analysis
"""

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


class Visualizer:
    """Generate visualization plots for analysis results."""

    def __init__(self, figsize=(14, 10), dpi=100):
        """
        Initialize visualizer.

        Args:
            figsize: Default figure size (width, height)
            dpi: Resolution in dots per inch
        """
        self.figsize = figsize
        self.dpi = dpi

        # Set style
        plt.style.use('dark_background')

    def generate_all(self, audio_path, y, sr, phase1, phase2, phase3, output_dir, asset_id):
        """
        Generate all visualization plots.

        Args:
            audio_path: Path to original audio file
            y: Audio time series
            sr: Sample rate
            phase1: PHASE 1 results
            phase2: PHASE 2 results
            phase3: PHASE 3 results
            output_dir: Output directory
            asset_id: Asset identifier

        Returns:
            list: Paths to generated plots
        """
        output_dir = Path(output_dir)
        viz_paths = []

        # 1. Comprehensive Overview
        path = self._plot_overview(
            y, sr, phase1, phase2, phase3, output_dir, asset_id
        )
        viz_paths.append(path)

        # 2. Mel Spectrogram with Artifacts
        path = self._plot_mel_spectrogram(
            phase3['mel_spectrogram_artifacts']['mel_spectrogram'],
            sr, output_dir, asset_id
        )
        viz_paths.append(path)

        # 3. Phase Plot (Time-Stretch Detection)
        path = self._plot_phase_analysis(
            phase3['phase_artifacts']['phase_data'],
            phase3['phase_artifacts']['magnitude_data'],
            sr, output_dir, asset_id
        )
        viz_paths.append(path)

        # 4. Pitch-Formant Comparison
        path = self._plot_pitch_formant_comparison(
            phase1, phase2, output_dir, asset_id
        )
        viz_paths.append(path)

        return viz_paths

    def _plot_overview(self, y, sr, phase1, phase2, phase3, output_dir, asset_id):
        """Create comprehensive overview plot with all key metrics."""
        fig, axes = plt.subplots(3, 2, figsize=self.figsize, dpi=self.dpi)
        fig.suptitle(f'Forensic Audio Analysis Overview: {asset_id}', fontsize=16, fontweight='bold')

        # 1. Waveform
        ax = axes[0, 0]
        librosa.display.waveshow(y, sr=sr, ax=ax, color='cyan')
        ax.set_title('Waveform')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')

        # 2. F0 Over Time
        ax = axes[0, 1]
        if len(phase1['f0_values']) > 0:
            ax.plot(phase1['f0_times'], phase1['f0_values'], color='yellow', linewidth=0.5)
            ax.axhline(y=phase1['f0_median'], color='red', linestyle='--',
                      label=f"Median: {phase1['f0_median']:.1f} Hz")
            ax.set_title(f"Fundamental Frequency (F0) - Presented as: {phase1['presented_sex']}")
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Frequency (Hz)')
            ax.legend()
            ax.grid(True, alpha=0.3)

        # 3. Mel Spectrogram
        ax = axes[1, 0]
        mel_spec = phase3['mel_spectrogram_artifacts']['mel_spectrogram']
        img = librosa.display.specshow(mel_spec, sr=sr, x_axis='time', y_axis='mel', ax=ax, cmap='magma')
        ax.set_title('Mel Spectrogram (Artifact Analysis)')
        fig.colorbar(img, ax=ax, format='%+2.0f dB')

        # 4. Formant Analysis
        ax = axes[1, 1]
        formant_labels = ['F1', 'F2', 'F3']
        formant_values = [
            phase2['f1_median'],
            phase2['f2_median'],
            phase2['f3_median']
        ]
        bars = ax.bar(formant_labels, formant_values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax.set_title(f"Formants - Probable Sex: {phase2['probable_sex']}")
        ax.set_ylabel('Frequency (Hz)')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, value in zip(bars, formant_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.0f} Hz', ha='center', va='bottom')

        # 5. Detection Summary
        ax = axes[2, 0]
        ax.axis('off')

        incoherence = phase3['pitch_formant_incoherence']
        mel_artifacts = phase3['mel_spectrogram_artifacts']
        phase_artifacts = phase3['phase_artifacts']

        summary_text = f"""
DETECTION SUMMARY
{'━' * 40}

Pitch-Formant Incoherence:
  {'✓ DETECTED' if incoherence['incoherence_detected'] else '✗ Not detected'}
  Confidence: {incoherence['confidence']:.0%}

Spectral Artifacts:
  {'✓ DETECTED' if mel_artifacts['artifacts_detected'] else '✗ Not detected'}
  Noise Floor: {mel_artifacts['noise_floor_std']:.2f}
  Spectral Smoothness: {mel_artifacts['spectral_smoothness']:.2f}

Time-Stretch Artifacts:
  {'✓ DETECTED' if phase_artifacts['transient_smearing_detected'] else '✗ Not detected'}
  Phase Variance: {phase_artifacts['phase_variance']:.2f}
  Onset Sharpness: {phase_artifacts['onset_sharpness']:.2f}
        """
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', family='monospace',
               bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

        # 6. Overall Verdict
        ax = axes[2, 1]
        ax.axis('off')

        manipulation_detected = phase3['overall_manipulation_detected']
        verdict_color = '#FF4444' if manipulation_detected else '#44FF44'
        verdict_text = 'MANIPULATION\nDETECTED' if manipulation_detected else 'NO MANIPULATION\nDETECTED'

        ax.text(0.5, 0.5, verdict_text, transform=ax.transAxes,
               fontsize=24, fontweight='bold', ha='center', va='center',
               color=verdict_color,
               bbox=dict(boxstyle='round', facecolor='#1a1a1a',
                        edgecolor=verdict_color, linewidth=3, alpha=0.8))

        plt.tight_layout()
        output_path = output_dir / f"{asset_id}_overview.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return output_path

    def _plot_mel_spectrogram(self, mel_spec, sr, output_dir, asset_id):
        """Plot detailed mel spectrogram for artifact inspection."""
        fig, ax = plt.subplots(figsize=(12, 6), dpi=self.dpi)

        img = librosa.display.specshow(mel_spec, sr=sr, x_axis='time', y_axis='mel',
                                      ax=ax, cmap='magma')
        ax.set_title('Mel Spectrogram - Artifact Analysis\n' +
                    'Look for: Unnatural harmonics, consistent noise floor, spectral discontinuities',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        fig.colorbar(img, ax=ax, format='%+2.0f dB', label='Magnitude (dB)')

        plt.tight_layout()
        output_path = output_dir / f"{asset_id}_mel_spectrogram.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return output_path

    def _plot_phase_analysis(self, phase_data, magnitude_data, sr, output_dir, asset_id):
        """Plot phase analysis for time-stretch artifact detection."""
        fig, axes = plt.subplots(2, 1, figsize=(12, 10), dpi=self.dpi)

        # Magnitude spectrogram
        ax = axes[0]
        magnitude_db = librosa.amplitude_to_db(magnitude_data, ref=np.max)
        img = librosa.display.specshow(magnitude_db, sr=sr, x_axis='time', y_axis='hz',
                                      ax=ax, cmap='viridis')
        ax.set_title('STFT Magnitude', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency (Hz)')
        fig.colorbar(img, ax=ax, format='%+2.0f dB')

        # Phase plot
        ax = axes[1]
        img = librosa.display.specshow(phase_data, sr=sr, x_axis='time', y_axis='hz',
                                      ax=ax, cmap='twilight', vmin=-np.pi, vmax=np.pi)
        ax.set_title('Phase Plot - Time-Stretch Detection\n' +
                    'Natural audio: random static-like. Time-stretched: structured vertical artifacts.',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        fig.colorbar(img, ax=ax, label='Phase (radians)')

        plt.tight_layout()
        output_path = output_dir / f"{asset_id}_phase_analysis.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return output_path

    def _plot_pitch_formant_comparison(self, phase1, phase2, output_dir, asset_id):
        """Plot pitch-formant comparison to visualize incoherence."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=self.dpi)

        # Expected ranges for male/female
        male_f0_range = (85, 180)
        female_f0_range = (165, 255)
        male_formants = {'F1': (400, 800), 'F2': (1000, 1500)}
        female_formants = {'F1': (600, 1000), 'F2': (1400, 2200)}

        # F0 comparison
        ax = axes[0]
        ax.barh(['Male Range', 'Female Range'],
               [male_f0_range[1] - male_f0_range[0],
                female_f0_range[1] - female_f0_range[0]],
               left=[male_f0_range[0], female_f0_range[0]],
               color=['#4A90E2', '#E94B8B'], alpha=0.5, height=0.4)

        # Plot actual F0
        actual_f0 = phase1['f0_median']
        ax.plot([actual_f0, actual_f0], [0, 1], 'r-', linewidth=3,
               label=f'Actual F0: {actual_f0:.1f} Hz')
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Male Range', 'Female Range'])
        ax.set_xlabel('Frequency (Hz)')
        ax.set_title(f"F0 Analysis - Presented as: {phase1['presented_sex']}", fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')

        # Formant comparison
        ax = axes[1]
        x_positions = np.arange(2)
        width = 0.35

        # Male ranges
        ax.bar(x_positions - width/2,
              [male_formants['F1'][1] - male_formants['F1'][0],
               male_formants['F2'][1] - male_formants['F2'][0]],
              width,
              bottom=[male_formants['F1'][0], male_formants['F2'][0]],
              label='Male Range', color='#4A90E2', alpha=0.5)

        # Female ranges
        ax.bar(x_positions + width/2,
              [female_formants['F1'][1] - female_formants['F1'][0],
               female_formants['F2'][1] - female_formants['F2'][0]],
              width,
              bottom=[female_formants['F1'][0], female_formants['F2'][0]],
              label='Female Range', color='#E94B8B', alpha=0.5)

        # Actual formants
        actual_formants = [phase2['f1_median'], phase2['f2_median']]
        ax.plot(x_positions, actual_formants, 'ro-', linewidth=2, markersize=10,
               label='Actual Formants')

        ax.set_xticks(x_positions)
        ax.set_xticklabels(['F1', 'F2'])
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"Formant Analysis - Probable Sex: {phase2['probable_sex']}", fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = output_dir / f"{asset_id}_pitch_formant_comparison.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return output_path
