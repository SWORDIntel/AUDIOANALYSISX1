"""
TUI - TEXT USER INTERFACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Interactive terminal interface for Voice Manipulation Detection Pipeline
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
import time

from ..pipeline import VoiceManipulationDetector


console = Console()


def print_banner():
    """Display ASCII banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗   ██╗ ██████╗ ██╗ ██████╗███████╗    ███╗   ███╗██████╗ ██████╗     ║
║   ██║   ██║██╔═══██╗██║██╔════╝██╔════╝    ████╗ ████║██╔══██╗██╔══██╗    ║
║   ██║   ██║██║   ██║██║██║     █████╗      ██╔████╔██║██║  ██║██║  ██║    ║
║   ╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝      ██║╚██╔╝██║██║  ██║██║  ██║    ║
║    ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗    ██║ ╚═╝ ██║██████╔╝██████╔╝    ║
║     ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝    ╚═╝     ╚═╝╚═════╝ ╚═════╝     ║
║                                                                              ║
║              FORENSIC AUDIO MANIPULATION DETECTION SYSTEM                   ║
║                  Tactical Implementation Specification                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def create_sitrep_panel(asset_id, duration, sample_rate):
    """Create SITREP (Situation Report) panel."""
    content = f"""
[bold yellow]THREATCON:[/bold yellow] CHARLIE
[bold yellow]MISSION:[/bold yellow] Forensic Analysis & Alteration Detection

[bold cyan]ASSET INTELLIGENCE:[/bold cyan]
  • ID: {asset_id}
  • Duration: {duration:.2f} seconds
  • Sample Rate: {sample_rate} Hz
  • Status: LOADED - ANALYSIS PENDING

[bold red]THREAT ASSESSMENT:[/bold red]
  Potential adversarial manipulation detected.
  F0 (pitch) considered UNRELIABLE.
  Multi-phase verification required.
    """
    return Panel(content, title="[bold red]⚠ SITREP ⚠[/bold red]", border_style="red", box=box.DOUBLE)


def create_phase_table(phase_num, title, status, findings=None):
    """Create phase status table."""
    table = Table(title=f"[bold]PHASE {phase_num}: {title}[/bold]", box=box.ROUNDED, border_style="cyan")

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="yellow")
    table.add_column("Status", style="green")

    if findings:
        for metric, value, status_text in findings:
            table.add_row(metric, value, status_text)
    else:
        table.add_row("Status", status, "⏳ PENDING")

    return table


def create_detection_panel(report):
    """Create final detection verdict panel."""
    alteration = report['ALTERATION_DETECTED']

    if alteration:
        style = "bold red on black"
        symbol = "⚠ ALERT ⚠"
        verdict = "MANIPULATION DETECTED"
        color = "red"
    else:
        style = "bold green on black"
        symbol = "✓ CLEAR ✓"
        verdict = "NO MANIPULATION DETECTED"
        color = "green"

    content = f"""
[{style}]{symbol}[/{style}]

[bold {color}]{verdict}[/bold {color}]

[bold]CONFIDENCE:[/bold] {report['CONFIDENCE']}

[bold]EVIDENCE VECTORS:[/bold]
  [1] PITCH: {report['EVIDENCE_VECTOR_1_PITCH']}
  [2] TIME: {report['EVIDENCE_VECTOR_2_TIME']}
  [3] SPECTRAL: {report['EVIDENCE_VECTOR_3_SPECTRAL']}

[bold]CLASSIFICATION:[/bold]
  • Presented As: {report['PRESENTED_AS']}
  • Probable Sex: {report['PROBABLE_SEX']}
  • F0 Baseline: {report['DECEPTION_BASELINE_F0']}
  • Formants: {report['PHYSICAL_BASELINE_FORMANTS']}
    """

    return Panel(content, title=f"[bold {color}]FINAL VERDICT[/bold {color}]",
                border_style=color, box=box.DOUBLE)


def display_phase_progress(phase_name, phase_results):
    """Display phase results in a formatted table."""
    if phase_name == "PHASE 1":
        findings = [
            ("F0 Median", f"{phase_results['f0_median']:.1f} Hz", "✓"),
            ("F0 Mean", f"{phase_results['f0_mean']:.1f} Hz", "✓"),
            ("F0 Std Dev", f"{phase_results['f0_std']:.2f} Hz", "✓"),
            ("Presented As", phase_results['presented_sex'], "✓")
        ]
        table = create_phase_table(1, "BASELINE ANALYSIS", "COMPLETE", findings)
        console.print(table)

    elif phase_name == "PHASE 2":
        findings = [
            ("F1 Formant", f"{phase_results['f1_median']:.0f} Hz", "✓"),
            ("F2 Formant", f"{phase_results['f2_median']:.0f} Hz", "✓"),
            ("F3 Formant", f"{phase_results['f3_median']:.0f} Hz", "✓"),
            ("Probable Sex", phase_results['probable_sex'], "✓")
        ]
        table = create_phase_table(2, "VOCAL TRACT ANALYSIS", "COMPLETE", findings)
        console.print(table)

    elif phase_name == "PHASE 3":
        incoherence = phase_results['pitch_formant_incoherence']['incoherence_detected']
        mel_artifacts = phase_results['mel_spectrogram_artifacts']['artifacts_detected']
        phase_artifacts = phase_results['phase_artifacts']['transient_smearing_detected']

        findings = [
            ("Pitch-Formant Incoherence",
             "DETECTED" if incoherence else "Not Detected",
             "⚠ ALERT" if incoherence else "✓"),
            ("Spectral Artifacts",
             "DETECTED" if mel_artifacts else "Not Detected",
             "⚠ ALERT" if mel_artifacts else "✓"),
            ("Time-Stretch Artifacts",
             "DETECTED" if phase_artifacts else "Not Detected",
             "⚠ ALERT" if phase_artifacts else "✓"),
            ("Overall Manipulation",
             "DETECTED" if phase_results['overall_manipulation_detected'] else "Not Detected",
             "⚠ ALERT" if phase_results['overall_manipulation_detected'] else "✓")
        ]
        table = create_phase_table(3, "ARTIFACT & COHERENCE ANALYSIS", "COMPLETE", findings)
        console.print(table)


@click.group()
def cli():
    """Voice Manipulation Detection - Forensic Audio Analysis System"""
    pass


@cli.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./results', help='Output directory for results')
@click.option('--no-viz', is_flag=True, help='Disable visualization generation')
def analyze(audio_file, output_dir, no_viz):
    """Analyze a single audio file for voice manipulation."""
    print_banner()

    audio_path = Path(audio_file)
    asset_id = audio_path.stem

    console.print("\n[bold cyan]═══ MISSION INITIATION ═══[/bold cyan]\n")

    # Load audio metadata
    import librosa
    y, sr = librosa.load(str(audio_path), sr=None)
    duration = len(y) / sr

    # Display SITREP
    console.print(create_sitrep_panel(asset_id, duration, sr))
    console.print()

    # Initialize detector
    detector = VoiceManipulationDetector()

    # Progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        # Phase 1
        task1 = progress.add_task("[cyan]PHASE 1: Baseline Analysis...", total=100)
        phase1_results = detector.phase1.analyze(y, sr)
        progress.update(task1, completed=100)

    display_phase_progress("PHASE 1", phase1_results)
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        # Phase 2
        task2 = progress.add_task("[cyan]PHASE 2: Vocal Tract Analysis...", total=100)
        phase2_results = detector.phase2.analyze(str(audio_path), sr)
        progress.update(task2, completed=100)

    display_phase_progress("PHASE 2", phase2_results)
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        # Phase 3
        task3 = progress.add_task("[cyan]PHASE 3: Artifact Analysis...", total=100)
        phase3_results = detector.phase3.analyze(y, sr, phase1_results, phase2_results)
        progress.update(task3, completed=100)

    display_phase_progress("PHASE 3", phase3_results)
    console.print()

    # Phase 4
    console.print("[bold cyan]PHASE 4: Report Synthesis[/bold cyan]")
    report = detector.phase4.synthesize(asset_id, phase1_results, phase2_results, phase3_results)

    # Save report
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{asset_id}_report.json"
    detector.phase4.save_report(report, report_path)

    console.print(f"  ✓ Report saved: [cyan]{report_path}[/cyan]")

    # Generate visualizations
    if not no_viz:
        from visualizer import Visualizer
        console.print("  [yellow]⏳ Generating visualizations...[/yellow]")
        viz = Visualizer()
        viz_paths = viz.generate_all(
            audio_path, y, sr,
            phase1_results, phase2_results, phase3_results,
            output_dir, asset_id
        )
        console.print(f"  ✓ Visualizations saved: [cyan]{len(viz_paths)} plots[/cyan]")

    console.print()

    # Display final verdict
    console.print(create_detection_panel(report))


@cli.command()
@click.argument('audio_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./batch_results', help='Output directory for results')
@click.option('--pattern', '-p', default='*.wav', help='File pattern to match')
def batch(audio_dir, output_dir, pattern):
    """Batch analyze multiple audio files in a directory."""
    print_banner()

    audio_dir = Path(audio_dir)
    audio_files = list(audio_dir.glob(pattern))

    if not audio_files:
        console.print(f"[red]Error: No files found matching pattern '{pattern}'[/red]")
        return

    console.print(f"\n[bold cyan]═══ BATCH ANALYSIS: {len(audio_files)} FILES ═══[/bold cyan]\n")

    detector = VoiceManipulationDetector()
    results_summary = []

    with Progress(console=console) as progress:
        overall_task = progress.add_task(
            "[cyan]Processing files...",
            total=len(audio_files)
        )

        for audio_file in audio_files:
            progress.update(overall_task, description=f"[cyan]Processing: {audio_file.name}")

            try:
                report = detector.analyze(audio_file, output_dir, save_visualizations=False)
                results_summary.append({
                    'file': audio_file.name,
                    'manipulated': report['ALTERATION_DETECTED'],
                    'confidence': report['CONFIDENCE']
                })
            except Exception as e:
                console.print(f"  [red]✗ Error processing {audio_file.name}: {e}[/red]")

            progress.advance(overall_task)

    # Display summary table
    console.print("\n[bold cyan]═══ BATCH ANALYSIS SUMMARY ═══[/bold cyan]\n")

    summary_table = Table(title="Analysis Results", box=box.ROUNDED, border_style="cyan")
    summary_table.add_column("File", style="cyan")
    summary_table.add_column("Manipulation", style="yellow")
    summary_table.add_column("Confidence", style="green")

    for result in results_summary:
        status = "[red]DETECTED[/red]" if result['manipulated'] else "[green]CLEAN[/green]"
        summary_table.add_row(result['file'], status, result['confidence'])

    console.print(summary_table)

    # Statistics
    total = len(results_summary)
    manipulated = sum(1 for r in results_summary if r['manipulated'])
    clean = total - manipulated

    stats_panel = Panel(
        f"""
[bold]Total Files Analyzed:[/bold] {total}
[bold red]Manipulated Detected:[/bold red] {manipulated} ({manipulated/total*100:.1f}%)
[bold green]Clean Files:[/bold green] {clean} ({clean/total*100:.1f}%)
        """,
        title="[bold]Statistics[/bold]",
        border_style="cyan"
    )
    console.print(stats_panel)


@cli.command()
def interactive():
    """Interactive mode with menu-driven interface."""
    print_banner()

    while True:
        console.print("\n[bold cyan]═══ MAIN MENU ═══[/bold cyan]\n")
        console.print("1. Analyze Single File")
        console.print("2. Batch Analysis")
        console.print("3. Create Test Sample")
        console.print("4. Exit")

        choice = Prompt.ask("\n[bold yellow]Select option[/bold yellow]", choices=["1", "2", "3", "4"])

        if choice == "1":
            audio_file = Prompt.ask("[cyan]Enter audio file path[/cyan]")
            output_dir = Prompt.ask("[cyan]Enter output directory[/cyan]", default="./results")
            no_viz = not Confirm.ask("[cyan]Generate visualizations?[/cyan]", default=True)

            if Path(audio_file).exists():
                analyze.callback(audio_file, output_dir, no_viz)
            else:
                console.print(f"[red]Error: File not found: {audio_file}[/red]")

        elif choice == "2":
            audio_dir = Prompt.ask("[cyan]Enter audio directory path[/cyan]")
            output_dir = Prompt.ask("[cyan]Enter output directory[/cyan]", default="./batch_results")
            pattern = Prompt.ask("[cyan]Enter file pattern[/cyan]", default="*.wav")

            if Path(audio_dir).exists():
                batch.callback(audio_dir, output_dir, pattern)
            else:
                console.print(f"[red]Error: Directory not found: {audio_dir}[/red]")

        elif choice == "3":
            console.print("[yellow]Generating test sample with known manipulation...[/yellow]")
            from example import example_create_test_sample
            example_create_test_sample()

        elif choice == "4":
            console.print("\n[bold cyan]Mission Complete. Exiting...[/bold cyan]\n")
            break


if __name__ == '__main__':
    cli()
