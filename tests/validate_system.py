#!/usr/bin/env python3
"""
DEBUG & VALIDATION SUITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Comprehensive validation of all AUDIOANALYSISX1 components

This script validates:
- All Python modules import correctly
- All dependencies are installed
- File structure is correct
- Pipeline functionality
- GUI components
- Sample files exist
- Documentation is present
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


class DebugValidator:
    """Comprehensive system validation."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def print_header(self):
        """Print validation header."""
        console.print("\n[bold cyan]" + "=" * 80 + "[/bold cyan]")
        console.print("[bold cyan]AUDIOANALYSISX1 - DEBUG & VALIDATION SUITE[/bold cyan]")
        console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]\n")

    def check_dependencies(self):
        """Check all required dependencies."""
        console.print("[bold yellow]📦 Checking Dependencies...[/bold yellow]\n")

        deps = {
            'librosa': 'Audio analysis',
            'numpy': 'Numerical computing',
            'scipy': 'Signal processing',
            'matplotlib': 'Visualizations',
            'parselmouth': 'Formant extraction',
            'soundfile': 'Audio I/O',
            'rich': 'Terminal UI',
            'click': 'CLI framework',
            'gradio': 'Web GUI',
            'pandas': 'Data tables'
        }

        for module, purpose in deps.items():
            try:
                __import__(module)
                console.print(f"  ✓ {module:20} - {purpose}")
                self.passed.append(f"Dependency: {module}")
            except ImportError:
                console.print(f"  [red]✗ {module:20} - {purpose}[/red]")
                self.errors.append(f"Missing dependency: {module}")

        console.print()

    def check_modules(self):
        """Check all project modules."""
        console.print("[bold yellow]🐍 Checking Python Modules...[/bold yellow]\n")

        modules = [
            ('phase1_baseline', 'BaselineAnalyzer'),
            ('phase2_formants', 'VocalTractAnalyzer'),
            ('phase3_artifacts', 'ArtifactAnalyzer'),
            ('phase4_report', 'ReportSynthesizer'),
            ('phase5_ai_detection', 'AIVoiceDetector'),
            ('pipeline', 'VoiceManipulationDetector'),
            ('verification', 'OutputVerifier'),
            ('visualizer', 'Visualizer'),
            ('gui_utils', None),
            ('gui_app', 'AudioAnalysisGUI')
        ]

        for module_name, class_name in modules:
            try:
                module = __import__(module_name)
                if class_name:
                    getattr(module, class_name)
                console.print(f"  ✓ {module_name:25} ({class_name or 'utilities'})")
                self.passed.append(f"Module: {module_name}")
            except Exception as e:
                console.print(f"  [red]✗ {module_name:25} - {str(e)}[/red]")
                self.errors.append(f"Module error: {module_name} - {e}")

        console.print()

    def check_files(self):
        """Check all required files exist."""
        console.print("[bold yellow]📁 Checking File Structure...[/bold yellow]\n")

        required_files = [
            'README.md',
            'GETTING_STARTED.md',
            'QUICKSTART.md',
            'GUI_GUIDE.md',
            'USAGE.md',
            'TECHNICAL.md',
            'API.md',
            'DEPLOYMENT.md',
            'requirements.txt',
            'pipeline.py',
            'phase1_baseline.py',
            'phase2_formants.py',
            'phase3_artifacts.py',
            'phase4_report.py',
            'phase5_ai_detection.py',
            'verification.py',
            'visualizer.py',
            'gui_app.py',
            'gui_utils.py',
            'start_gui.py',
            'analyze.py',
            'tui.py',
            'download_samples.py'
        ]

        for filename in required_files:
            path = Path(filename)
            if path.exists():
                size = path.stat().st_size
                console.print(f"  ✓ {filename:30} ({size:,} bytes)")
                self.passed.append(f"File: {filename}")
            else:
                console.print(f"  [red]✗ {filename:30} MISSING[/red]")
                self.errors.append(f"Missing file: {filename}")

        console.print()

    def check_directories(self):
        """Check required directories."""
        console.print("[bold yellow]📂 Checking Directories...[/bold yellow]\n")

        dirs = ['samples', 'samples/human', 'samples/tts', 'samples/manipulated']

        for dirname in dirs:
            path = Path(dirname)
            if path.exists() and path.is_dir():
                file_count = len(list(path.glob('*.wav')))
                console.print(f"  ✓ {dirname:30} ({file_count} WAV files)")
                self.passed.append(f"Directory: {dirname}")
            else:
                console.print(f"  [yellow]⚠ {dirname:30} (not created)[/yellow]")
                self.warnings.append(f"Directory missing: {dirname}")

        console.print()

    def test_basic_functionality(self):
        """Test basic pipeline functionality."""
        console.print("[bold yellow]🧪 Testing Basic Functionality...[/bold yellow]\n")

        try:
            # Test import
            from pipeline import VoiceManipulationDetector
            console.print("  ✓ Pipeline import successful")

            # Create detector
            detector = VoiceManipulationDetector()
            console.print("  ✓ Detector initialization successful")

            # Check phases exist
            assert hasattr(detector, 'phase1'), "Phase 1 missing"
            assert hasattr(detector, 'phase2'), "Phase 2 missing"
            assert hasattr(detector, 'phase3'), "Phase 3 missing"
            assert hasattr(detector, 'phase4'), "Phase 4 (AI) missing"
            assert hasattr(detector, 'phase5'), "Phase 5 missing"
            console.print("  ✓ All 5 phases initialized")

            # Check verifier
            assert hasattr(detector, 'verifier'), "Verifier missing"
            console.print("  ✓ Verification system loaded")

            self.passed.append("Basic functionality test")

        except Exception as e:
            console.print(f"  [red]✗ Functionality test failed: {e}[/red]")
            self.errors.append(f"Functionality error: {e}")

        console.print()

    def test_sample_files(self):
        """Check sample audio files."""
        console.print("[bold yellow]🎵 Checking Sample Files...[/bold yellow]\n")

        sample_dir = Path('samples')
        if not sample_dir.exists():
            console.print("  [yellow]⚠ Samples directory not found[/yellow]")
            console.print("  [yellow]  Run: python download_samples.py[/yellow]")
            self.warnings.append("No sample files found")
            console.print()
            return

        categories = ['human', 'tts', 'manipulated', 'voice_cloning', 'deepfake']

        for category in categories:
            cat_path = sample_dir / category
            if cat_path.exists():
                wav_files = list(cat_path.glob('*.wav'))
                mp3_files = list(cat_path.glob('*.mp3'))
                total = len(wav_files) + len(mp3_files)

                if total > 0:
                    console.print(f"  ✓ {category:20} - {total} files")
                    self.passed.append(f"Samples: {category}")
                else:
                    console.print(f"  [yellow]⚠ {category:20} - 0 files[/yellow]")

        console.print()

    def test_gui_components(self):
        """Test GUI components."""
        console.print("[bold yellow]🌐 Testing GUI Components...[/bold yellow]\n")

        try:
            import gradio as gr
            console.print(f"  ✓ Gradio version: {gr.__version__}")

            from gui_app import AudioAnalysisGUI
            console.print("  ✓ AudioAnalysisGUI import successful")

            from gui_utils import format_results_html, create_batch_summary_df
            console.print("  ✓ GUI utilities import successful")

            self.passed.append("GUI components test")

        except Exception as e:
            console.print(f"  [red]✗ GUI test failed: {e}[/red]")
            self.errors.append(f"GUI error: {e}")

        console.print()

    def print_summary(self):
        """Print validation summary."""
        console.print("\n[bold cyan]" + "=" * 80 + "[/bold cyan]")
        console.print("[bold cyan]VALIDATION SUMMARY[/bold cyan]")
        console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]\n")

        # Create summary table
        table = Table(title="Results", box=box.ROUNDED, show_header=True, border_style="cyan")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Count", justify="right")
        table.add_column("Status", justify="center")

        # Passed
        passed_status = "[green]✓ PASSED[/green]" if len(self.passed) > 0 else "[red]✗ NONE[/red]"
        table.add_row("Passed", str(len(self.passed)), passed_status)

        # Warnings
        warn_status = "[yellow]⚠ WARNINGS[/yellow]" if len(self.warnings) > 0 else "[green]✓ NONE[/green]"
        table.add_row("Warnings", str(len(self.warnings)), warn_status)

        # Errors
        error_status = "[red]✗ ERRORS[/red]" if len(self.errors) > 0 else "[green]✓ NONE[/green]"
        table.add_row("Errors", str(len(self.errors)), error_status)

        console.print(table)

        # Detailed errors/warnings
        if self.errors:
            console.print("\n[bold red]ERRORS:[/bold red]")
            for error in self.errors:
                console.print(f"  • {error}")

        if self.warnings:
            console.print("\n[bold yellow]WARNINGS:[/bold yellow]")
            for warning in self.warnings:
                console.print(f"  • {warning}")

        # Overall status
        console.print()
        if len(self.errors) == 0:
            console.print(Panel(
                "[bold green]✅ ALL SYSTEMS OPERATIONAL[/bold green]\n\n"
                "The AUDIOANALYSISX1 system is ready for use!\n\n"
                "Quick start:\n"
                "  1. python download_samples.py (if not done)\n"
                "  2. python start_gui.py\n"
                "  3. Open browser and analyze audio files",
                title="[bold green]SUCCESS[/bold green]",
                border_style="green",
                box=box.DOUBLE
            ))
            return 0
        else:
            console.print(Panel(
                f"[bold red]❌ VALIDATION FAILED[/bold red]\n\n"
                f"Found {len(self.errors)} error(s) that must be fixed.\n\n"
                f"Common fixes:\n"
                f"  • pip install -r requirements.txt\n"
                f"  • python download_samples.py\n"
                f"  • Check error messages above",
                title="[bold red]ERRORS DETECTED[/bold red]",
                border_style="red",
                box=box.DOUBLE
            ))
            return 1

    def run(self):
        """Run complete validation suite."""
        self.print_header()

        self.check_dependencies()
        self.check_modules()
        self.check_files()
        self.check_directories()
        self.test_sample_files()
        self.test_basic_functionality()
        self.test_gui_components()

        return self.print_summary()


def main():
    """Main entry point."""
    validator = DebugValidator()
    return validator.run()


if __name__ == '__main__':
    sys.exit(main())
