#!/usr/bin/env python3
"""
AUDIOANALYSISX1 - Simple CLI Interface
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Easy-to-use command-line interface for voice analysis

Usage:
    python analyze.py <audio_file>
    python analyze.py --batch <directory>
    python analyze.py --help
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from pipeline import VoiceManipulationDetector


console = Console()


def print_banner():
    """Print application banner."""
    banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║                   AUDIOANALYSISX1                            ║
║          Voice Manipulation & AI Detection System            ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]
"""
    console.print(banner)


def analyze_single_file(audio_path, output_dir='results', show_viz=True):
    """
    Analyze a single audio file.

    Args:
        audio_path: Path to audio file
        output_dir: Output directory for results
        show_viz: Whether to generate visualizations
    """
    print_banner()

    audio_path = Path(audio_path)
    if not audio_path.exists():
        console.print(f"[red]✗ Error: File not found: {audio_path}[/red]")
        return 1

    console.print(f"\n[cyan]📁 Analyzing:[/cyan] {audio_path.name}")
    console.print(f"[cyan]📂 Output:[/cyan] {output_dir}/\n")

    try:
        detector = VoiceManipulationDetector()
        report = detector.analyze(
            str(audio_path),
            output_dir=output_dir,
            save_visualizations=show_viz
        )

        # Display results in a nice table
        display_results(report)

        console.print(f"\n[green]✓ Analysis complete![/green]")
        console.print(f"[cyan]📄 Full report:[/cyan] {output_dir}/{report['ASSET_ID']}_report.json")

        return 0

    except Exception as e:
        console.print(f"\n[red]✗ Error during analysis: {e}[/red]")
        return 1


def display_results(report):
    """Display analysis results in a formatted table."""
    console.print("\n" + "=" * 70)
    console.print("[bold]ANALYSIS RESULTS[/bold]")
    console.print("=" * 70 + "\n")

    # Main results table
    table = Table(title="Detection Summary", box=box.ROUNDED, show_header=True)
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Result", style="yellow")
    table.add_column("Details", style="white")

    # Voice characteristics
    table.add_row(
        "Voice Type",
        report['PRESENTED_AS'],
        f"F0: {report['DECEPTION_BASELINE_F0']}"
    )

    table.add_row(
        "Physical Characteristics",
        report['PROBABLE_SEX'],
        report['PHYSICAL_BASELINE_FORMANTS']
    )

    # Manipulation detection
    manip_status = "[red]DETECTED[/red]" if report['ALTERATION_DETECTED'] else "[green]NOT DETECTED[/green]"
    table.add_row(
        "Manipulation",
        manip_status,
        report['CONFIDENCE']
    )

    # AI detection
    ai_status = "[red]DETECTED[/red]" if report['AI_VOICE_DETECTED'] else "[green]NOT DETECTED[/green]"
    table.add_row(
        "AI Voice",
        ai_status,
        report['AI_TYPE']
    )

    console.print(table)

    # Evidence details
    if report['ALTERATION_DETECTED'] or report['AI_VOICE_DETECTED']:
        console.print("\n[bold red]⚠ EVIDENCE DETECTED:[/bold red]")

        if report['EVIDENCE_VECTOR_1_PITCH'] != "No pitch-formant incoherence detected":
            console.print(f"  [1] {report['EVIDENCE_VECTOR_1_PITCH']}")

        if report['EVIDENCE_VECTOR_2_TIME'] != "No time-stretch artifacts detected":
            console.print(f"  [2] {report['EVIDENCE_VECTOR_2_TIME']}")

        if report['EVIDENCE_VECTOR_3_SPECTRAL'] != "No spectral artifacts detected":
            console.print(f"  [3] {report['EVIDENCE_VECTOR_3_SPECTRAL']}")

        if report['AI_VOICE_DETECTED']:
            console.print(f"  [4] {report['EVIDENCE_VECTOR_4_AI']}")


def analyze_batch(directory, output_dir='batch_results', pattern='*.wav'):
    """
    Analyze multiple audio files in a directory.

    Args:
        directory: Directory containing audio files
        output_dir: Output directory for results
        pattern: File pattern to match
    """
    print_banner()

    directory = Path(directory)
    if not directory.exists():
        console.print(f"[red]✗ Error: Directory not found: {directory}[/red]")
        return 1

    audio_files = list(directory.rglob(pattern))
    if not audio_files:
        console.print(f"[red]✗ No files found matching pattern: {pattern}[/red]")
        return 1

    console.print(f"\n[cyan]📁 Analyzing {len(audio_files)} files from:[/cyan] {directory}")
    console.print(f"[cyan]📂 Output:[/cyan] {output_dir}/\n")

    detector = VoiceManipulationDetector()
    results = []

    for i, audio_file in enumerate(audio_files, 1):
        console.print(f"\n[cyan][{i}/{len(audio_files)}][/cyan] {audio_file.name}")

        try:
            report = detector.analyze(
                str(audio_file),
                output_dir=f"{output_dir}/{audio_file.stem}",
                save_visualizations=False  # Faster batch processing
            )
            results.append({
                'file': audio_file.name,
                'manipulated': report['ALTERATION_DETECTED'],
                'ai_detected': report['AI_VOICE_DETECTED'],
                'ai_type': report['AI_TYPE'],
                'confidence': report['CONFIDENCE']
            })
            console.print(f"  ✓ Complete")
        except Exception as e:
            console.print(f"  [red]✗ Error: {e}[/red]")
            results.append({
                'file': audio_file.name,
                'manipulated': None,
                'ai_detected': None,
                'ai_type': 'Error',
                'confidence': 'N/A'
            })

    # Display summary
    display_batch_summary(results)

    console.print(f"\n[green]✓ Batch analysis complete![/green]")
    console.print(f"[cyan]📂 Results:[/cyan] {output_dir}/")

    return 0


def display_batch_summary(results):
    """Display batch analysis summary."""
    console.print("\n" + "=" * 70)
    console.print("[bold]BATCH ANALYSIS SUMMARY[/bold]")
    console.print("=" * 70 + "\n")

    # Summary table
    table = Table(title="Results", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Manipulation", style="yellow")
    table.add_column("AI Voice", style="magenta")
    table.add_column("AI Type", style="white")
    table.add_column("Confidence", style="green")

    for result in results:
        manip = "[red]YES[/red]" if result['manipulated'] else "[green]NO[/green]"
        ai = "[red]YES[/red]" if result['ai_detected'] else "[green]NO[/green]"

        table.add_row(
            result['file'],
            manip,
            ai,
            result['ai_type'],
            result['confidence']
        )

    console.print(table)

    # Statistics
    total = len(results)
    manipulated = sum(1 for r in results if r['manipulated'])
    ai_detected = sum(1 for r in results if r['ai_detected'])
    clean = total - manipulated - ai_detected

    stats = f"""
[bold]Statistics:[/bold]
  Total Files: {total}
  Manipulated: {manipulated} ({manipulated/total*100:.1f}%)
  AI-Generated: {ai_detected} ({ai_detected/total*100:.1f}%)
  Clean: {clean} ({clean/total*100:.1f}%)
"""

    console.print(Panel(stats, title="Summary", border_style="cyan"))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AUDIOANALYSISX1 - Voice Manipulation & AI Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze.py sample.wav
  python analyze.py sample.wav --output ./results
  python analyze.py --batch samples/ --pattern "*.mp3"
  python analyze.py --batch samples/ --no-viz

For interactive mode:
  python tui.py interactive
        """
    )

    parser.add_argument(
        'audio',
        nargs='?',
        help='Audio file to analyze (or directory with --batch)'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch mode: analyze all files in directory'
    )

    parser.add_argument(
        '-o', '--output',
        default='results',
        help='Output directory (default: results/)'
    )

    parser.add_argument(
        '-p', '--pattern',
        default='*.wav',
        help='File pattern for batch mode (default: *.wav)'
    )

    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Disable visualization generation'
    )

    args = parser.parse_args()

    if not args.audio:
        parser.print_help()
        return 1

    if args.batch:
        return analyze_batch(args.audio, args.output, args.pattern)
    else:
        return analyze_single_file(args.audio, args.output, not args.no_viz)


if __name__ == '__main__':
    sys.exit(main())
