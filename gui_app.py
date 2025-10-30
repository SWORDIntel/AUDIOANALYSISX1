"""
GRADIO WEB GUI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modern web-based interface for AUDIOANALYSISX1
"""

import gradio as gr
import json
from pathlib import Path
import tempfile
import shutil

from pipeline import VoiceManipulationDetector
from gui_utils import (
    format_results_html,
    create_batch_summary_df,
    export_batch_csv,
    create_status_message,
    get_visualization_paths,
    format_evidence_list,
    create_detection_badge
)


class AudioAnalysisGUI:
    """Gradio web interface for voice analysis."""

    def __init__(self):
        self.detector = VoiceManipulationDetector()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="audioanalysis_"))

    def analyze_single_file(self, audio_file, progress=gr.Progress()):
        """
        Analyze a single audio file with progress updates.

        Args:
            audio_file: Uploaded audio file
            progress: Gradio progress tracker

        Returns:
            tuple: (html_results, json_download, md_download, viz1, viz2, viz3, viz4, evidence_md, badge_html)
        """
        if audio_file is None:
            return (
                "<div style='color: red;'>❌ Please upload an audio file</div>",
                None, None, None, None, None, None, "", ""
            )

        try:
            # Update progress
            progress(0, desc="Loading audio file...")

            # Get file path
            audio_path = Path(audio_file.name if hasattr(audio_file, 'name') else audio_file)
            asset_id = audio_path.stem

            # Create output directory
            output_dir = self.temp_dir / asset_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # Load audio
            import librosa
            progress(0.1, desc=create_status_message(1, "processing"))
            y, sr = librosa.load(str(audio_path), sr=None)

            # PHASE 1
            progress(0.2, desc=create_status_message(1, "processing"))
            phase1_results = self.detector.phase1.analyze(y, sr)
            progress(0.3, desc=create_status_message(1, "complete"))

            # PHASE 2
            progress(0.4, desc=create_status_message(2, "processing"))
            phase2_results = self.detector.phase2.analyze(str(audio_path), sr)
            progress(0.5, desc=create_status_message(2, "complete"))

            # PHASE 3
            progress(0.6, desc=create_status_message(3, "processing"))
            phase3_results = self.detector.phase3.analyze(y, sr, phase1_results, phase2_results)
            progress(0.7, desc=create_status_message(3, "complete"))

            # PHASE 4 - AI Detection
            progress(0.75, desc=create_status_message(4, "processing"))
            phase4_results = self.detector.phase4.analyze(y, sr)
            progress(0.85, desc=create_status_message(4, "complete"))

            # PHASE 5 - Report Synthesis
            progress(0.9, desc=create_status_message(5, "processing"))
            report = self.detector.phase5.synthesize(
                asset_id, phase1_results, phase2_results, phase3_results, phase4_results
            )

            # Add verification
            report = self.detector.verifier.sign_report(report, audio_path)

            # Save reports
            json_path = output_dir / f"{asset_id}_report.json"
            md_path = output_dir / f"{asset_id}_report.md"

            self.detector.phase5.save_report(report, json_path)
            self.detector.exporter.export_markdown(report, md_path)

            # Generate visualizations
            progress(0.95, desc="Generating visualizations...")
            from visualizer import Visualizer
            viz = Visualizer()
            viz.generate_all(
                audio_path, y, sr,
                phase1_results, phase2_results, phase3_results,
                output_dir, asset_id
            )

            progress(1.0, desc="✓ Analysis complete!")

            # Get visualization paths
            viz_paths = get_visualization_paths(output_dir, asset_id)

            # Format results
            html_results = format_results_html(report)
            evidence_md = format_evidence_list(report)
            badge_html = create_detection_badge(report)

            return (
                badge_html + html_results,
                str(json_path),
                str(md_path),
                viz_paths.get('overview'),
                viz_paths.get('mel_spectrogram'),
                viz_paths.get('phase_analysis'),
                viz_paths.get('pitch_formant'),
                evidence_md,
                f"Analysis timestamp: {report['ANALYSIS_TIMESTAMP']}"
            )

        except Exception as e:
            error_html = f"""
            <div style='background: #ff4444; color: white; padding: 20px; border-radius: 10px;'>
                <h3>❌ Analysis Error</h3>
                <p>{str(e)}</p>
            </div>
            """
            return (error_html, None, None, None, None, None, None, "", str(e))

    def analyze_batch(self, files, progress=gr.Progress()):
        """
        Analyze multiple audio files.

        Args:
            files: List of uploaded audio files
            progress: Gradio progress tracker

        Returns:
            tuple: (summary_html, summary_table, csv_download)
        """
        if not files:
            return (
                "<div style='color: red;'>❌ Please upload audio files</div>",
                None,
                None
            )

        try:
            reports = []
            total = len(files)

            for i, audio_file in enumerate(files):
                progress((i / total), desc=f"Processing {i+1}/{total}: {Path(audio_file.name).name}")

                audio_path = Path(audio_file.name if hasattr(audio_file, 'name') else audio_file)
                asset_id = audio_path.stem
                output_dir = self.temp_dir / "batch" / asset_id

                try:
                    report = self.detector.analyze(
                        str(audio_path),
                        output_dir=str(output_dir),
                        save_visualizations=False  # Faster for batch
                    )
                    reports.append(report)
                except Exception as e:
                    print(f"Error processing {asset_id}: {e}")

            progress(1.0, desc="✓ Batch analysis complete!")

            # Create summary
            df = create_batch_summary_df(reports)

            # Export CSV
            csv_path = self.temp_dir / f"batch_summary_{len(reports)}_files.csv"
            export_batch_csv(reports, csv_path)

            # Statistics
            total_count = len(reports)
            manip_count = sum(1 for r in reports if r['ALTERATION_DETECTED'])
            ai_count = sum(1 for r in reports if r['AI_VOICE_DETECTED'])
            clean_count = total_count - max(manip_count, ai_count)

            summary_html = f"""
            <div style="font-family: monospace; background: #1a1a1a; padding: 20px; border-radius: 10px; color: #e0e0e0;">
                <h2 style="color: #00ffff;">📊 BATCH ANALYSIS SUMMARY</h2>
                <table style="width: 100%; margin: 20px 0;">
                    <tr style="background: #2a2a2a;">
                        <td style="padding: 10px;"><strong>Total Files:</strong></td>
                        <td style="padding: 10px; color: #00ffff;">{total_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;"><strong>Manipulated:</strong></td>
                        <td style="padding: 10px; color: #ff4444;">{manip_count} ({manip_count/total_count*100:.1f}%)</td>
                    </tr>
                    <tr style="background: #2a2a2a;">
                        <td style="padding: 10px;"><strong>AI-Generated:</strong></td>
                        <td style="padding: 10px; color: #ff8844;">{ai_count} ({ai_count/total_count*100:.1f}%)</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;"><strong>Clean:</strong></td>
                        <td style="padding: 10px; color: #44ff44;">{clean_count} ({clean_count/total_count*100:.1f}%)</td>
                    </tr>
                </table>
            </div>
            """

            return (summary_html, df, str(csv_path))

        except Exception as e:
            error_html = f"<div style='color: red;'>❌ Batch processing error: {str(e)}</div>"
            return (error_html, None, None)

    def build_interface(self):
        """Build the complete Gradio interface."""

        # Custom CSS
        custom_css = """
        .gradio-container {
            font-family: 'Courier New', monospace !important;
        }
        .primary-btn {
            background: linear-gradient(90deg, #00ffff, #0088ff) !important;
            border: none !important;
            font-weight: bold !important;
        }
        """

        with gr.Blocks(theme=gr.themes.Monochrome(), css=custom_css, title="AUDIOANALYSISX1") as app:

            # Header
            gr.Markdown("""
            # 🔬 AUDIOANALYSISX1
            ## Voice Manipulation & AI Detection System

            **Forensic audio analysis with 5-phase detection pipeline**

            - 🎵 Detects pitch-shifting and time-stretching
            - 🤖 Detects AI-generated voices (TTS, voice cloning, deepfakes)
            - 🔒 Cryptographically verified outputs
            - 📊 Comprehensive visualizations
            """)

            with gr.Tabs() as tabs:

                # TAB 1: Single File Analysis
                with gr.Tab("🎵 Single File Analysis"):
                    gr.Markdown("### Upload an audio file to analyze for voice manipulation and AI generation")

                    with gr.Row():
                        with gr.Column(scale=1):
                            audio_input = gr.Audio(
                                label="Upload Audio File",
                                type="filepath",
                                sources=["upload"]
                            )

                            analyze_btn = gr.Button(
                                "🔍 Analyze Audio",
                                variant="primary",
                                size="lg"
                            )

                            gr.Markdown("""
                            **Supported formats:** WAV, MP3, FLAC, OGG, M4A
                            **Optimal length:** 3-10 seconds
                            **Max size:** 100 MB
                            """)

                        with gr.Column(scale=2):
                            status_text = gr.Textbox(
                                label="Status",
                                value="Ready to analyze...",
                                interactive=False
                            )

                            badge_output = gr.HTML(label="Detection Status")
                            results_output = gr.HTML(label="Analysis Results")

                    with gr.Row():
                        evidence_output = gr.Markdown("Upload a file to see evidence details")

                    gr.Markdown("### 📊 Visualizations")

                    with gr.Row():
                        viz_overview = gr.Image(label="Overview Dashboard", type="filepath")
                        viz_mel = gr.Image(label="Mel Spectrogram", type="filepath")

                    with gr.Row():
                        viz_phase = gr.Image(label="Phase Analysis", type="filepath")
                        viz_pitch_formant = gr.Image(label="Pitch-Formant Comparison", type="filepath")

                    gr.Markdown("### 📥 Download Reports")

                    with gr.Row():
                        json_download = gr.File(label="JSON Report (with verification)")
                        md_download = gr.File(label="Markdown Report")

                    # Connect analyze button
                    analyze_btn.click(
                        fn=self.analyze_single_file,
                        inputs=[audio_input],
                        outputs=[
                            results_output,
                            json_download,
                            md_download,
                            viz_overview,
                            viz_mel,
                            viz_phase,
                            viz_pitch_formant,
                            evidence_output,
                            status_text
                        ]
                    )

                # TAB 2: Batch Processing
                with gr.Tab("📁 Batch Processing"):
                    gr.Markdown("### Upload multiple audio files for batch analysis")

                    batch_files = gr.File(
                        label="Upload Audio Files",
                        file_count="multiple",
                        type="filepath"
                    )

                    batch_analyze_btn = gr.Button(
                        "🔍 Analyze Batch",
                        variant="primary",
                        size="lg"
                    )

                    batch_summary_html = gr.HTML(label="Summary Statistics")

                    batch_results_table = gr.Dataframe(
                        label="Detailed Results",
                        headers=["File", "Manipulation", "AI Voice", "AI Type", "Confidence", "Presented As", "Probable Sex"],
                        interactive=False
                    )

                    batch_csv_download = gr.File(label="Download CSV Summary")

                    # Connect batch button
                    batch_analyze_btn.click(
                        fn=self.analyze_batch,
                        inputs=[batch_files],
                        outputs=[
                            batch_summary_html,
                            batch_results_table,
                            batch_csv_download
                        ]
                    )

                # TAB 3: About & Help
                with gr.Tab("📖 About & Help"):
                    gr.Markdown("""
                    # 🔬 AUDIOANALYSISX1
                    ## Forensic Audio Manipulation Detection System

                    ---

                    ### 🎯 What Does This Do?

                    This system analyzes audio files to detect:

                    1. **Voice Manipulation**
                       - Pitch-shifting (male ↔ female voice conversion)
                       - Time-stretching (speed manipulation)
                       - Combined attacks

                    2. **AI-Generated Voices**
                       - Text-to-Speech (TTS) systems
                       - Voice cloning
                       - Neural vocoders (WaveNet, WaveGlow, HiFi-GAN)
                       - Deepfakes

                    ---

                    ### 🔍 Detection Methods

                    #### Phase 1: Baseline F0 Analysis
                    Extracts fundamental frequency (pitch) to determine presented voice characteristics.

                    #### Phase 2: Vocal Tract Analysis
                    Extracts formants (F1, F2, F3) - physical vocal tract resonances that cannot be easily manipulated.

                    #### Phase 3: Manipulation Detection
                    - **Pitch-Formant Incoherence:** Detects when pitch doesn't match physical characteristics
                    - **Spectral Artifacts:** Finds unnatural harmonics and noise patterns
                    - **Phase Decoherence:** Detects time-stretching artifacts

                    #### Phase 4: AI Voice Detection
                    - **Neural Vocoder Artifacts:** High-frequency analysis, spectral rolloff
                    - **Prosody Analysis:** Detects unnaturally smooth pitch contours
                    - **Breathing Detection:** Finds lack of natural breath sounds
                    - **Micro-timing:** Detects overly perfect timing
                    - **Harmonic Analysis:** Unnatural harmonic-to-noise ratios
                    - **Statistical Features:** MFCC and zero-crossing rate anomalies

                    #### Phase 5: Report Synthesis
                    Consolidates findings with cryptographic verification (SHA-256 checksums).

                    ---

                    ### 📊 Understanding Confidence Levels

                    | Confidence | Meaning |
                    |------------|---------|
                    | **95-99%** | Very High - Multiple independent methods confirm detection |
                    | **85-94%** | High - Strong evidence from multiple sources |
                    | **60-84%** | Medium - Some indicators detected |
                    | **<60%** | Low - Inconclusive, review carefully |

                    ---

                    ### 💡 How to Interpret Results

                    **"Presented As" vs "Probable Sex"**
                    - **Presented As:** Based on pitch (F0) - can be manipulated
                    - **Probable Sex:** Based on formants - physical characteristics that are hard to fake
                    - **Mismatch = Evidence of manipulation!**

                    **AI Type Classifications:**
                    - **Neural Vocoder:** WaveNet, WaveGlow, HiFi-GAN artifacts
                    - **TTS System:** Tacotron, FastSpeech, VITS characteristics
                    - **Voice Cloning:** Real-Time VC, SV2TTS patterns
                    - **Advanced Deepfake:** Multi-stage synthesis

                    ---

                    ### 🛡️ Security & Privacy

                    - ✅ All processing is local (no data sent to servers)
                    - ✅ Uploaded files are temporary (auto-deleted)
                    - ✅ Cryptographic verification of all outputs
                    - ✅ Read-only audio file operations

                    ---

                    ### 📚 Documentation

                    For complete documentation, see:
                    - `README.md` - Project overview
                    - `GETTING_STARTED.md` - Quick start guide
                    - `TECHNICAL.md` - Technical details
                    - `API.md` - API reference

                    ---

                    ### ⚖️ Ethical Use

                    This tool is for **authorized forensic analysis, security research, and testing only**.

                    - Obtain proper authorization before analyzing recordings
                    - Comply with applicable laws and regulations
                    - Respect privacy and consent requirements

                    ---

                    **Version:** 1.0.0
                    **Pipeline:** 5-Phase Detection
                    **Methods:** 9 Independent Detection Techniques
                    **Repository:** AUDIOANALYSISX1 (Private)
                    """)

            # Footer
            gr.Markdown("""
            ---
            <div style='text-align: center; color: #888;'>
                <p>🔬 Built with Gradio for forensic audio analysis</p>
                <p>For command-line usage: <code>python analyze.py audio.wav</code></p>
            </div>
            """)

        return app

    def launch(self, share=False, server_port=7860):
        """
        Launch the Gradio interface.

        Args:
            share: Create shareable public link
            server_port: Port to run server on

        Returns:
            Gradio app instance
        """
        app = self.build_interface()
        app.launch(
            share=share,
            server_port=server_port,
            show_error=True,
            inbrowser=True  # Auto-open browser
        )
        return app


def main():
    """Launch the GUI application."""
    import sys

    # Parse arguments
    share = '--share' in sys.argv
    port = 7860

    for arg in sys.argv:
        if arg.startswith('--port='):
            port = int(arg.split('=')[1])

    print("\n" + "=" * 80)
    print("AUDIOANALYSISX1 - Web GUI")
    print("=" * 80 + "\n")
    print(f"🚀 Starting web interface on port {port}...")
    print(f"🌐 Open your browser to: http://localhost:{port}")

    if share:
        print("🔗 Share mode enabled - public link will be generated")

    print("\nPress Ctrl+C to stop the server")
    print("=" * 80 + "\n")

    gui = AudioAnalysisGUI()
    gui.launch(share=share, server_port=port)


if __name__ == '__main__':
    main()
