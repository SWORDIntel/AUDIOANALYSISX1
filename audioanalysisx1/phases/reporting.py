"""
PHASE 4: SYNTHESIS & FINAL REPORT (AUGMENTED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Synthesize all data points into comprehensive forensic report
"""

import json
from datetime import datetime
from pathlib import Path
from ..verification import sanitize_for_json


class ReportSynthesizer:
    """Synthesizes analysis results into comprehensive forensic report."""

    def __init__(self):
        self.report_template = {
            'ASSET_ID': None,
            'ANALYSIS_TIMESTAMP': None,
            'DECEPTION_BASELINE_F0': None,
            'PRESENTED_AS': None,
            'PHYSICAL_BASELINE_FORMANTS': None,
            'PROBABLE_SEX': None,
            'ALTERATION_DETECTED': None,
            'EVIDENCE_VECTOR_1_PITCH': None,
            'EVIDENCE_VECTOR_2_TIME': None,
            'EVIDENCE_VECTOR_3_SPECTRAL': None,
            'CONFIDENCE': None,
            'DETAILED_FINDINGS': None
        }

    def synthesize(self, asset_id, phase1, phase2, phase3, phase4):
        """
        Create comprehensive forensic report from all phases.

        Args:
            asset_id: Audio file identifier
            phase1: PHASE 1 results (baseline F0)
            phase2: PHASE 2 results (formants)
            phase3: PHASE 3 results (artifacts)
            phase4: PHASE 4 results (AI detection)

        Returns:
            dict: Comprehensive forensic report
        """
        # Extract key metrics
        f0_median = phase1['f0_median']
        presented_sex = phase1['presented_sex']

        f1_median = phase2['f1_median']
        f2_median = phase2['f2_median']
        f3_median = phase2['f3_median']
        probable_sex = phase2['probable_sex']

        incoherence = phase3['pitch_formant_incoherence']
        mel_artifacts = phase3['mel_spectrogram_artifacts']
        phase_artifacts = phase3['phase_artifacts']

        # AI detection results
        ai_detected = phase4['ai_detected']
        ai_confidence = phase4['confidence']
        ai_type = phase4['ai_type']

        # Determine overall alteration status (manipulation OR AI)
        alteration_detected = phase3['overall_manipulation_detected'] or ai_detected

        # Calculate confidence score
        confidence = self._calculate_confidence(incoherence, mel_artifacts, phase_artifacts, ai_detected, ai_confidence)

        # Build evidence vectors
        evidence_pitch = self._build_pitch_evidence(incoherence)
        evidence_time = self._build_time_evidence(phase_artifacts)
        evidence_spectral = self._build_spectral_evidence(mel_artifacts)
        evidence_ai = self._build_ai_evidence(phase4)

        # Generate detailed findings
        detailed_findings = self._generate_detailed_findings(
            phase1, phase2, phase3, phase4, alteration_detected
        )

        # Construct report
        report = {
            'asset_id': asset_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'f0_baseline': f"{f0_median:.1f} Hz",
            'presented_sex': presented_sex,
            'formant_baseline': {
                'f1': f"{f1_median:.0f} Hz",
                'f2': f"{f2_median:.0f} Hz",
                'f3': f"{f3_median:.0f} Hz",
            },
            'probable_sex': probable_sex,
            'alteration_detected': alteration_detected,
            'ai_voice_detected': ai_detected,
            'ai_voice_type': ai_type,
            'confidence': {
                'score': confidence,
                'label': self._confidence_label(confidence)
            },
            'evidence': {
                'pitch': evidence_pitch,
                'time': evidence_time,
                'spectral': evidence_spectral,
                'ai': evidence_ai,
            },
            'summary': detailed_findings['summary'],
            'details': detailed_findings
        }

        return report

    def _calculate_confidence(self, incoherence, mel_artifacts, phase_artifacts, ai_detected, ai_confidence):
        """
        Calculate overall confidence score based on evidence strength.

        Multiple independent detection methods increase confidence.
        """
        evidence_count = sum([
            incoherence['incoherence_detected'],
            mel_artifacts['artifacts_detected'],
            phase_artifacts['transient_smearing_detected'],
            ai_detected
        ])

        if evidence_count == 0:
            return 0.0
        elif evidence_count == 1:
            # Single vector - medium confidence
            if ai_detected:
                return ai_confidence
            else:
                base_confidence = max(
                    incoherence.get('confidence', 0),
                    0.60 if mel_artifacts['artifacts_detected'] else 0,
                    0.65 if phase_artifacts['transient_smearing_detected'] else 0
                )
                return base_confidence
        elif evidence_count == 2:
            # Two vectors - high confidence
            return 0.85
        elif evidence_count == 3:
            # Three vectors - very high confidence
            return 0.95
        else:
            # All four vectors - maximum confidence
            return 0.99

    def _confidence_label(self, confidence):
        """Convert confidence score to label."""
        if confidence >= 0.90:
            return "Very High"
        elif confidence >= 0.75:
            return "High"
        elif confidence >= 0.50:
            return "Medium"
        else:
            return "Low"

    def _build_pitch_evidence(self, incoherence):
        """Build evidence string for pitch manipulation."""
        if incoherence['incoherence_detected']:
            return f"Pitch-Formant Incoherence Detected. {incoherence['evidence']}"
        else:
            return "No pitch-formant incoherence detected"

    def _build_time_evidence(self, phase_artifacts):
        """Build evidence string for time manipulation."""
        if phase_artifacts['transient_smearing_detected']:
            return f"Phase Decoherence / Transient Smearing Detected. {phase_artifacts['evidence']}"
        else:
            return "No time-stretch artifacts detected"

    def _build_spectral_evidence(self, mel_artifacts):
        """Build evidence string for spectral manipulation."""
        if mel_artifacts['artifacts_detected']:
            return f"Spectral Artifacts Detected. {mel_artifacts['evidence']}"
        else:
            return "No spectral artifacts detected"

    def _build_ai_evidence(self, phase4):
        """Build evidence string for AI voice detection."""
        if phase4['ai_detected']:
            confidence = f"{phase4['confidence']:.0%}"
            ai_type = phase4['ai_type']
            return f"AI Voice Detected ({ai_type}, {confidence} confidence)."
        else:
            return "No AI voice artifacts detected"

    def _generate_detailed_findings(self, phase1, phase2, phase3, phase4, alteration_detected):
        """Generate detailed findings section."""
        findings = {
            'summary': self._generate_summary(alteration_detected, phase1, phase2, phase4),
            'phase1_baseline': {
                'f0_median': phase1['f0_median'],
                'f0_mean': phase1['f0_mean'],
                'f0_std': phase1['f0_std'],
                'presented_sex': phase1['presented_sex']
            },
            'phase2_formants': {
                'f1_median': phase2['f1_median'],
                'f2_median': phase2['f2_median'],
                'f3_median': phase2['f3_median'],
                'probable_sex': phase2['probable_sex']
            },
            'phase3_artifacts': {
                'pitch_formant_incoherence': {
                    'detected': phase3['pitch_formant_incoherence']['incoherence_detected'],
                    'confidence': phase3['pitch_formant_incoherence']['confidence'],
                    'evidence': phase3['pitch_formant_incoherence']['evidence']
                },
                'mel_spectrogram': {
                    'artifacts_detected': phase3['mel_spectrogram_artifacts']['artifacts_detected'],
                    'consistent_noise_floor': phase3['mel_spectrogram_artifacts']['consistent_noise_floor'],
                    'unnatural_harmonics': phase3['mel_spectrogram_artifacts']['unnatural_harmonics']
                },
                'phase_coherence': {
                    'time_stretch_detected': phase3['phase_artifacts']['transient_smearing_detected'],
                    'phase_variance': phase3['phase_artifacts']['phase_variance'],
                    'onset_sharpness': phase3['phase_artifacts']['onset_sharpness'],
                    'transient_smearing': phase3['phase_artifacts']['transient_smearing']
                }
            },
            'phase4_ai_detection': {
                'ai_detected': phase4['ai_detected'],
                'ai_type': phase4['ai_type'],
                'confidence': phase4['confidence']
            }
        }

        return findings

    def _generate_summary(self, alteration_detected, phase1, phase2, phase4=None):
        """Generate executive summary."""
        if alteration_detected:
            base_msg = (
                f"MANIPULATION DETECTED: Audio presents as {phase1['presented_sex']} "
                f"(F0: {phase1['f0_median']:.1f} Hz) but physical vocal tract "
                f"characteristics indicate {phase2['probable_sex']} "
                f"(F1: {phase2['f1_median']:.0f} Hz). "
            )

            if phase4 and phase4['ai_detected']:
                base_msg += f"AI voice detected: {phase4['ai_type']}. "

            base_msg += "Multiple independent artifact detection methods confirm alteration."
            return base_msg
        else:
            return (
                f"NO MANIPULATION DETECTED: Audio characteristics are coherent. "
                f"Presented sex ({phase1['presented_sex']}) matches "
                f"physical characteristics ({phase2['probable_sex']})."
            )

    def save_report(self, report, output_path):
        """
        Save report to JSON file.

        Args:
            report: Report dictionary
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sanitize report for JSON serialization
        report_sanitized = sanitize_for_json(report)

        with open(output_path, 'w') as f:
            json.dump(report_sanitized, f, indent=2)

    def print_report(self, report):
        """
        Print formatted report to console.

        Args:
            report: Report dictionary
        """
        # --- Helper for color coding ---
        def get_color(text, color_code):
            return f"\033[{color_code}m{text}\033[0m"

        # --- Colors ---
        HEADER = '1;94'
        SECTION = '1;96'
        LABEL = '1;97'
        PASS = '1;92'
        FAIL = '1;91'
        INFO = '93'

        # --- Report Data ---
        asset_id = report['asset_id']
        timestamp = report['timestamp']
        alteration_detected = report['alteration_detected']
        confidence = report['confidence']['score']
        confidence_label = report['confidence']['label']

        # --- Header ---
        print("\n" + get_color(" " * 80, '44'))
        print(get_color(f" F O R E N S I C   A U D I O   A N A L Y S I S", HEADER))
        print(get_color("=" * 80, '1;94'))
        print(f"{get_color('Asset ID:', LABEL)} {asset_id}")
        print(f"{get_color('Timestamp:', LABEL)} {timestamp}")
        print(get_color("-" * 80, '94'))


        # --- Primary Findings ---
        print(get_color("\n[ P R I M A R Y   F I N D I N G S ]", SECTION))
        if alteration_detected:
            print(f"{get_color('Status:', LABEL)}      {get_color('ALTERATION DETECTED', FAIL)}")
        else:
            print(f"{get_color('Status:', LABEL)}      {get_color('No Alteration Detected', PASS)}")
        print(f"{get_color('Confidence:', LABEL)} {confidence:.0%} ({confidence_label})")


        # --- Vocal Profile ---
        print(get_color("\n[ V O C A L   P R O F I L E ]", SECTION))
        print(f"{get_color('Pitch (F0):', LABEL)}     {report['f0_baseline']} (Presented as {report['presented_sex']})")
        print(f"{get_color('Formants (Phys):', LABEL)} F1: {report['formant_baseline']['f1']}, F2: {report['formant_baseline']['f2']} (Probable Sex: {report['probable_sex']})")


        # --- Evidence Summary ---
        print(get_color("\n[ E V I D E N C E   S U M M A R Y ]", SECTION))
        print(f"  {'Pitch:'.ljust(10)} {report['evidence']['pitch']}")
        print(f"  {'Time:'.ljust(10)} {report['evidence']['time']}")
        print(f"  {'Spectral:'.ljust(10)} {report['evidence']['spectral']}")
        print(f"  {'AI Voice:'.ljust(10)} {report['evidence']['ai']}")


        # --- Executive Summary ---
        print(get_color("\n[ E X E C U T I V E   S U M M A R Y ]", SECTION))
        print(get_color(report['summary'], INFO))
        print(get_color(" " * 80, '44'))
        print()
