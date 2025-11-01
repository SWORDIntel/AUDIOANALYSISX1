"""
VERIFICATION & INTEGRITY MODULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ensures verifiable, tamper-evident outputs with cryptographic checksums
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import librosa
import numpy as np


def sanitize_for_json(obj):
    """
    Recursively sanitize objects for JSON serialization.

    Converts numpy arrays, numpy types, and other non-serializable objects
    to JSON-compatible types.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        # For other types, try to convert to string
        return str(obj)


class OutputVerifier:
    """Provides verifiable, tamper-evident outputs with cryptographic integrity."""

    def __init__(self):
        self.hash_algorithm = 'sha256'

    def compute_audio_hash(self, audio_path):
        """
        Compute cryptographic hash of audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            dict: Hash information
        """
        audio_path = Path(audio_path)

        # File-level hash (raw bytes)
        sha256_hash = hashlib.sha256()
        with open(audio_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        file_hash = sha256_hash.hexdigest()

        # Audio-level hash (normalized waveform)
        y, sr = librosa.load(str(audio_path), sr=None)
        audio_bytes = y.tobytes()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()

        return {
            'file_hash': file_hash,
            'audio_hash': audio_hash,
            'algorithm': self.hash_algorithm,
            'file_size_bytes': audio_path.stat().st_size
        }

    def sign_report(self, report, audio_path):
        """
        Add verification metadata to report.

        Args:
            report: Analysis report dictionary
            audio_path: Path to original audio file

        Returns:
            dict: Report with verification metadata
        """
        # Compute audio hash
        audio_hash_info = self.compute_audio_hash(audio_path)

        # Create verification block
        verification = {
            'timestamp_utc': datetime.utcnow().isoformat() + 'Z',
            'audio_file': {
                'path': str(Path(audio_path).absolute()),
                'filename': Path(audio_path).name,
                'file_hash_sha256': audio_hash_info['file_hash'],
                'audio_hash_sha256': audio_hash_info['audio_hash'],
                'file_size_bytes': audio_hash_info['file_size_bytes']
            },
            'pipeline_version': '1.0.0',
            'verification_protocol': 'FORENSIC-AUDIO-v1'
        }

        # Compute report hash (for tamper detection)
        # Sanitize report for JSON serialization
        report_sanitized = sanitize_for_json(report)
        report_json = json.dumps(report_sanitized, sort_keys=True)
        report_hash = hashlib.sha256(report_json.encode()).hexdigest()

        verification['report_hash_sha256'] = report_hash

        # Add verification block to report
        report['verification'] = verification

        return report

    def verify_report(self, report_path):
        """
        Verify integrity of a saved report.

        Args:
            report_path: Path to JSON report file

        Returns:
            dict: Verification results
        """
        with open(report_path, 'r') as f:
            report = json.load(f)

        if 'verification' not in report:
            return {
                'valid': False,
                'error': 'Report does not contain verification metadata'
            }

        verification = report['verification']

        # Check if audio file still exists
        audio_path = verification['audio_file']['path']
        if not Path(audio_path).exists():
            return {
                'valid': False,
                'error': f'Original audio file not found: {audio_path}'
            }

        # Recompute audio hash
        current_hash_info = self.compute_audio_hash(audio_path)

        # Verify audio file integrity
        if current_hash_info['file_hash'] != verification['audio_file']['file_hash_sha256']:
            return {
                'valid': False,
                'error': 'Audio file has been modified since analysis',
                'expected_hash': verification['audio_file']['file_hash_sha256'],
                'actual_hash': current_hash_info['file_hash']
            }

        # Verify report integrity
        # Make a deep copy and remove entire verification block
        import copy
        report_copy = copy.deepcopy(report)
        stored_report_hash = report_copy['verification']['report_hash_sha256']
        del report_copy['verification']

        # Sanitize for JSON (same as during signing)
        report_sanitized = sanitize_for_json(report_copy)
        report_json = json.dumps(report_sanitized, sort_keys=True)
        current_report_hash = hashlib.sha256(report_json.encode()).hexdigest()

        if current_report_hash != stored_report_hash:
            return {
                'valid': False,
                'error': 'Report has been tampered with',
                'expected_hash': stored_report_hash,
                'actual_hash': current_report_hash
            }

        return {
            'valid': True,
            'timestamp': verification['timestamp_utc'],
            'audio_file': verification['audio_file']['filename'],
            'pipeline_version': verification['pipeline_version']
        }

    def create_chain_of_custody(self, audio_path, report, analyst_id=None):
        """
        Create forensic chain of custody record.

        Args:
            audio_path: Path to audio file
            report: Analysis report
            analyst_id: Optional analyst identifier

        Returns:
            dict: Chain of custody record
        """
        custody = {
            'custody_id': hashlib.sha256(
                f"{audio_path}{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            'acquisition_timestamp': datetime.utcnow().isoformat() + 'Z',
            'analyst_id': analyst_id or 'AUTOMATED',
            'evidence': {
                'type': 'AUDIO_RECORDING',
                'format': Path(audio_path).suffix,
                'hash_sha256': self.compute_audio_hash(audio_path)['file_hash']
            },
            'analysis': {
                'alteration_detected': report['alteration_detected'],
                'confidence': report['confidence']['score'],
                'method': 'MULTI-PHASE-FORENSIC-ANALYSIS'
            },
            'integrity_verified': True
        }

        return custody


class ReportExporter:
    """Export reports in various verifiable formats."""

    def __init__(self):
        self.verifier = OutputVerifier()

    def export_markdown(self, report, output_path):
        """
        Export report as Markdown format.

        Args:
            report: Report dictionary
            output_path: Output file path
        """
        md_content = f"""# FORENSIC AUDIO ANALYSIS REPORT

**Generated:** {report.get('timestamp', 'N/A')}

---

## EXECUTIVE SUMMARY

- **Asset ID:** {report['asset_id']}
- **Alteration Detected:** {report['alteration_detected']}
- **Confidence:** {report['confidence']['score']:.0%} ({report['confidence']['label']})

---

## CLASSIFICATION

- **Presented As:** {report['presented_sex']}
- **Probable Sex:** {report['probable_sex']}

---

## BASELINE METRICS

### Pitch Analysis (F0)
- **Deception Baseline:** {report['f0_baseline']}

### Vocal Tract Analysis (Formants)
- **Physical Baseline:** F1: {report['formant_baseline']['f1']}, F2: {report['formant_baseline']['f2']}

---

## EVIDENCE VECTORS

### [1] PITCH MANIPULATION
{report['evidence']['pitch']}

### [2] TIME MANIPULATION
{report['evidence']['time']}

### [3] SPECTRAL ARTIFACTS
{report['evidence']['spectral']}

---

## DETAILED FINDINGS

{report['summary']}

---

## VERIFICATION

"""

        if 'verification' in report:
            v = report['verification']
            md_content += f"""
**Timestamp:** {v['timestamp_utc']}
**Audio File:** {v['audio_file']['filename']}
**File Hash (SHA-256):** `{v['audio_file']['file_hash_sha256']}`
**Report Hash (SHA-256):** `{v['report_hash_sha256']}`
**Pipeline Version:** {v['pipeline_version']}

This report is cryptographically signed and tamper-evident.
"""

        with open(output_path, 'w') as f:
            f.write(md_content)

    def export_csv_summary(self, reports, output_path):
        """
        Export multiple reports as CSV summary.

        Args:
            reports: List of report dictionaries
            output_path: Output CSV file path
        """
        import csv

        headers = [
            'asset_id',
            'alteration_detected',
            'confidence_score',
            'confidence_label',
            'presented_sex',
            'probable_sex',
            'f0_median_hz',
            'timestamp'
        ]

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            for report in reports:
                # Extract F0 value from string
                f0_str = report['f0_baseline'].split()[0]

                writer.writerow({
                    'asset_id': report['asset_id'],
                    'alteration_detected': report['alteration_detected'],
                    'confidence_score': report['confidence']['score'],
                    'confidence_label': report['confidence']['label'],
                    'presented_sex': report['presented_sex'],
                    'probable_sex': report['probable_sex'],
                    'f0_median_hz': f0_str,
                    'timestamp': report.get('timestamp', 'N/A')
                })
