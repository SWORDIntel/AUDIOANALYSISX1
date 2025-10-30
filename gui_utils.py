"""
GUI UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Helper functions for Gradio web interface
"""

import json
from pathlib import Path
import pandas as pd
from datetime import datetime


def format_results_html(report):
    """
    Format analysis results as HTML for Gradio display.

    Args:
        report: Analysis report dictionary

    Returns:
        str: HTML formatted results
    """
    # Determine status colors
    manip_color = "red" if report['ALTERATION_DETECTED'] else "green"
    ai_color = "red" if report['AI_VOICE_DETECTED'] else "green"

    # Build HTML
    html = f"""
    <div style="font-family: monospace; background: #1a1a1a; padding: 20px; border-radius: 10px; color: #e0e0e0;">
        <h2 style="color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 10px;">
            🔬 ANALYSIS RESULTS
        </h2>

        <div style="margin: 20px 0;">
            <h3 style="color: #ffff00;">Voice Characteristics</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #2a2a2a;">
                    <td style="padding: 10px; border: 1px solid #444;"><strong>Presented As:</strong></td>
                    <td style="padding: 10px; border: 1px solid #444;">{report['PRESENTED_AS']}</td>
                    <td style="padding: 10px; border: 1px solid #444;">{report['DECEPTION_BASELINE_F0']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #444;"><strong>Physical Characteristics:</strong></td>
                    <td style="padding: 10px; border: 1px solid #444;">{report['PROBABLE_SEX']}</td>
                    <td style="padding: 10px; border: 1px solid #444;">{report['PHYSICAL_BASELINE_FORMANTS']}</td>
                </tr>
            </table>
        </div>

        <div style="margin: 20px 0;">
            <h3 style="color: #ffff00;">Detection Results</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #2a2a2a;">
                    <td style="padding: 10px; border: 1px solid #444;"><strong>Manipulation Detected:</strong></td>
                    <td style="padding: 10px; border: 1px solid #444; color: {manip_color}; font-weight: bold;">
                        {report['ALTERATION_DETECTED']}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #444;"><strong>AI Voice Detected:</strong></td>
                    <td style="padding: 10px; border: 1px solid #444; color: {ai_color}; font-weight: bold;">
                        {report['AI_VOICE_DETECTED']}
                    </td>
                </tr>
                <tr style="background: #2a2a2a;">
                    <td style="padding: 10px; border: 1px solid #444;"><strong>AI Type:</strong></td>
                    <td style="padding: 10px; border: 1px solid #444;">{report['AI_TYPE']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #444;"><strong>Confidence:</strong></td>
                    <td style="padding: 10px; border: 1px solid #444; color: #00ff00; font-weight: bold;">
                        {report['CONFIDENCE']}
                    </td>
                </tr>
            </table>
        </div>

        <div style="margin: 20px 0;">
            <h3 style="color: #ffff00;">Evidence Vectors</h3>
            <div style="background: #2a2a2a; padding: 15px; border-radius: 5px; border-left: 4px solid #00ffff;">
                <p><strong>[1] PITCH:</strong> {report['EVIDENCE_VECTOR_1_PITCH']}</p>
                <p><strong>[2] TIME:</strong> {report['EVIDENCE_VECTOR_2_TIME']}</p>
                <p><strong>[3] SPECTRAL:</strong> {report['EVIDENCE_VECTOR_3_SPECTRAL']}</p>
                <p><strong>[4] AI:</strong> {report['EVIDENCE_VECTOR_4_AI']}</p>
            </div>
        </div>

        <div style="margin: 20px 0; padding: 15px; background: #2a2a2a; border-radius: 5px;">
            <h4 style="color: #00ffff;">Summary</h4>
            <p>{report['DETAILED_FINDINGS']['summary']}</p>
        </div>
    </div>
    """

    return html


def create_batch_summary_df(reports):
    """
    Create pandas DataFrame from batch analysis results.

    Args:
        reports: List of report dictionaries

    Returns:
        pd.DataFrame: Summary table
    """
    data = []
    for report in reports:
        data.append({
            'File': report['ASSET_ID'],
            'Manipulation': '✓ YES' if report['ALTERATION_DETECTED'] else '✗ NO',
            'AI Voice': '✓ YES' if report['AI_VOICE_DETECTED'] else '✗ NO',
            'AI Type': report['AI_TYPE'],
            'Confidence': report['CONFIDENCE'],
            'Presented As': report['PRESENTED_AS'],
            'Probable Sex': report['PROBABLE_SEX']
        })

    return pd.DataFrame(data)


def export_batch_csv(reports, output_path):
    """
    Export batch results to CSV.

    Args:
        reports: List of report dictionaries
        output_path: Path to save CSV

    Returns:
        str: Path to saved CSV
    """
    df = create_batch_summary_df(reports)
    df.to_csv(output_path, index=False)
    return str(output_path)


def create_status_message(phase, status="processing"):
    """
    Create status message for progress updates.

    Args:
        phase: Phase number (1-5)
        status: Status string

    Returns:
        str: Formatted status message
    """
    phase_names = {
        1: "Baseline F0 Analysis",
        2: "Vocal Tract Formant Analysis",
        3: "Manipulation Artifact Detection",
        4: "AI Voice Detection",
        5: "Report Synthesis"
    }

    if status == "processing":
        icon = "⏳"
    elif status == "complete":
        icon = "✓"
    elif status == "warning":
        icon = "⚠"
    else:
        icon = "•"

    return f"{icon} PHASE {phase}: {phase_names.get(phase, 'Unknown')}"


def get_visualization_paths(output_dir, asset_id):
    """
    Get paths to all visualization files.

    Args:
        output_dir: Output directory path
        asset_id: Asset identifier

    Returns:
        dict: Paths to visualization files
    """
    output_dir = Path(output_dir)

    viz_files = {
        'overview': output_dir / f"{asset_id}_overview.png",
        'mel_spectrogram': output_dir / f"{asset_id}_mel_spectrogram.png",
        'phase_analysis': output_dir / f"{asset_id}_phase_analysis.png",
        'pitch_formant': output_dir / f"{asset_id}_pitch_formant_comparison.png"
    }

    # Return only files that exist
    return {k: str(v) for k, v in viz_files.items() if v.exists()}


def format_evidence_list(report):
    """
    Create markdown formatted evidence list.

    Args:
        report: Analysis report

    Returns:
        str: Markdown formatted evidence
    """
    evidence_md = "### 🔍 Evidence Summary\n\n"

    if report['ALTERATION_DETECTED'] or report['AI_VOICE_DETECTED']:
        evidence_md += "**⚠ THREATS DETECTED:**\n\n"

        if report['EVIDENCE_VECTOR_1_PITCH'] != "No pitch-formant incoherence detected":
            evidence_md += f"- **[PITCH]** {report['EVIDENCE_VECTOR_1_PITCH']}\n\n"

        if report['EVIDENCE_VECTOR_2_TIME'] != "No time-stretch artifacts detected":
            evidence_md += f"- **[TIME]** {report['EVIDENCE_VECTOR_2_TIME']}\n\n"

        if report['EVIDENCE_VECTOR_3_SPECTRAL'] != "No spectral artifacts detected":
            evidence_md += f"- **[SPECTRAL]** {report['EVIDENCE_VECTOR_3_SPECTRAL']}\n\n"

        if report['AI_VOICE_DETECTED']:
            evidence_md += f"- **[AI]** {report['EVIDENCE_VECTOR_4_AI']}\n\n"

        evidence_md += f"**Confidence:** {report['CONFIDENCE']}\n"
    else:
        evidence_md += "**✓ NO THREATS DETECTED**\n\n"
        evidence_md += "Audio appears to be a clean, unmanipulated human voice recording.\n"

    return evidence_md


def create_detection_badge(report):
    """
    Create status badge HTML.

    Args:
        report: Analysis report

    Returns:
        str: HTML badge
    """
    if report['ALTERATION_DETECTED'] or report['AI_VOICE_DETECTED']:
        return """
        <div style="background: #ff4444; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0;">
            ⚠ MANIPULATION OR AI DETECTED ⚠
        </div>
        """
    else:
        return """
        <div style="background: #44ff44; color: black; padding: 20px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0;">
            ✓ CLEAN VOICE VERIFIED ✓
        </div>
        """


def estimate_processing_time(file_size_mb):
    """
    Estimate processing time based on file size.

    Args:
        file_size_mb: File size in megabytes

    Returns:
        str: Estimated time string
    """
    # Rough estimate: 1 MB = ~3 seconds
    estimated_seconds = file_size_mb * 3

    if estimated_seconds < 5:
        return "~5 seconds"
    elif estimated_seconds < 30:
        return f"~{int(estimated_seconds)} seconds"
    elif estimated_seconds < 120:
        return f"~{int(estimated_seconds / 60)} minute(s)"
    else:
        return f"~{int(estimated_seconds / 60)} minutes"
