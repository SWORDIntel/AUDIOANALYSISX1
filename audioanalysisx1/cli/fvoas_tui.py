#!/usr/bin/env python3
"""
FVOAS TUI - Federal Voice Obfuscation and Analysis Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Terminal User Interface for real-time voice anonymization

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import click

try:
    from ..fvoas import FVOASController, ObfuscationMode
except ImportError:
    print("Error: FVOAS module not available")
    sys.exit(1)


console = Console()


def print_banner():
    """Display FVOAS banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ███████╗██╗   ██╗ ██████╗  █████╗ ███████╗                                ║
║   ██╔════╝██║   ██║██╔═══██╗██╔══██╗██╔════╝                                ║
║   █████╗  ██║   ██║██║   ██║███████║███████╗                                ║
║   ██╔══╝  ██║   ██║██║   ██║██╔══██║╚════██║                                ║
║   ██║     ╚██████╔╝╚██████╔╝██║  ██║███████║                                ║
║   ╚═╝      ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝                                ║
║                                                                              ║
║        FEDERAL VOICE OBFUSCATION AND ANALYSIS SUITE                         ║
║              Real-Time Voice Anonymization System                           ║
║                                                                              ║
║              Classification: SECRET | CNSA 2.0 Compliant                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def create_status_panel(controller: FVOASController) -> Panel:
    """Create status panel showing current FVOAS state."""
    try:
        stats = controller.get_stats()
        state = controller.get_state()
        
        # Get preset info
        current_preset = stats.get('current_preset', 'None')
        preset_info = FVOASController.list_presets().get(current_preset, {})
        
        # Hardware/Software mode
        hw_mode = "✓ HARDWARE" if stats.get('hardware_mode') else "⚠ SOFTWARE"
        mode_color = "green" if stats.get('hardware_mode') else "yellow"
        
        # Dynamic mode status
        dyn_enabled = stats.get('dynamic_enabled', False)
        dyn_status = "ENABLED" if dyn_enabled else "DISABLED"
        dyn_color = "green" if dyn_enabled else "white"
        
        # Crypto status
        crypto_status = "✓ AVAILABLE" if stats.get('crypto_available') else "⚠ UNAVAILABLE"
        crypto_color = "green" if stats.get('crypto_available') else "yellow"
        
        content = f"""
[bold cyan]SYSTEM STATUS:[/bold cyan]
  Mode: [{mode_color}]{hw_mode}[/{mode_color}]
  Preset: [yellow]{current_preset}[/yellow]
  Dynamic Mode: [{dyn_color}]{dyn_status}[/{dyn_color}]
  Crypto: [{crypto_color}]{crypto_status}[/{crypto_color}]
  
[bold cyan]SESSION INFO:[/bold cyan]
  Session ID: {stats.get('session_id', 'N/A')[:16]}...
  Uptime: {stats.get('uptime_seconds', 0):.1f}s
  Telemetry: {stats.get('telemetry_count', 0)} samples
  Threats Detected: {stats.get('threat_count', 0)}
  
[bold cyan]CURRENT PARAMETERS:[/bold cyan]
  Pitch: {preset_info.get('pitch_semitones', 0):+.2f} semitones
  Formant Ratio: {preset_info.get('formant_ratio', 1.0):.3f}
  Mode: {preset_info.get('mode', 'N/A')}
        """
        
        # Add dynamic state if enabled
        if dyn_enabled and 'dynamic' in stats:
            dyn = stats['dynamic']
            content += f"""
            
[bold cyan]DYNAMIC ANONYMIZATION:[/bold cyan]
  Target Profile: {dyn.get('target', 'N/A')}
  Target F0: {dyn.get('target_f0', 0):.1f} Hz
  Current F0: {dyn.get('current_f0', 0):.1f} Hz
  Pitch Adjustment: {dyn.get('pitch_adj', 0):+.2f} semitones
  Formant Ratio: {dyn.get('formant_adj', 1.0):.3f}
  Stability: {dyn.get('stability', 0):.0%}
  Profile Stable: {'✓' if dyn.get('stable') else '⚠'}
            """
        
        return Panel(content, title="[bold red]FVOAS STATUS[/bold red]", 
                    border_style="cyan", box=box.DOUBLE)
    except Exception as e:
        return Panel(f"[red]Error getting status: {e}[/red]", 
                    title="[bold red]ERROR[/bold red]", border_style="red")


def create_presets_table() -> Table:
    """Create table showing available presets."""
    presets = FVOASController.list_presets()
    
    table = Table(title="[bold]Available Anonymization Presets[/bold]", 
                 box=box.ROUNDED, border_style="cyan", show_header=True)
    table.add_column("Preset Name", style="cyan", no_wrap=True)
    table.add_column("Mode", style="yellow")
    table.add_column("Pitch", style="green")
    table.add_column("Formant", style="magenta")
    table.add_column("Description", style="white")
    
    # Sort: anonymization presets first, then others
    anon_presets = [(k, v) for k, v in presets.items() if 'anonymous' in k.lower() or 'dynamic' in k.lower()]
    other_presets = [(k, v) for k, v in presets.items() if k not in [p[0] for p in anon_presets]]
    
    for name, info in sorted(anon_presets) + sorted(other_presets):
        desc = info.get('description', '')
        if len(desc) > 50:
            desc = desc[:47] + "..."
        table.add_row(
            name,
            info.get('mode', 'N/A'),
            f"{info.get('pitch_semitones', 0):+.2f}",
            f"{info.get('formant_ratio', 1.0):.3f}",
            desc
        )
    
    return table


def create_telemetry_panel(telemetry) -> Optional[Panel]:
    """Create panel showing telemetry data."""
    if not telemetry:
        return Panel("[yellow]No telemetry available[/yellow]", 
                    title="[bold]TELEMETRY[/bold]", border_style="yellow")
    
    content = f"""
[bold cyan]VOICE CHARACTERISTICS:[/bold cyan]
  F0 (Fundamental): {telemetry.f0_median:.1f} Hz
  F1 Formant: {telemetry.formants[0]:.0f} Hz
  F2 Formant: {telemetry.formants[1]:.0f} Hz
  F3 Formant: {telemetry.formants[2]:.0f} Hz
  
[bold cyan]THREAT ANALYSIS:[/bold cyan]
  Manipulation Confidence: {telemetry.manipulation_confidence:.1%}
  AI Voice Probability: {telemetry.ai_voice_probability:.1%}
  
[bold cyan]SESSION:[/bold cyan]
  Session ID: {telemetry.session_id[:16]}...
    """
    
    return Panel(content, title="[bold]TELEMETRY[/bold]", 
                border_style="green", box=box.ROUNDED)


def realtime_dashboard(controller: FVOASController):
    """Display real-time dashboard."""
    print_banner()
    console.print("\n[bold cyan]Real-Time Anonymization Dashboard[/bold cyan]")
    console.print("[yellow]Press Ctrl+C to exit[/yellow]\n")
    
    try:
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                layout = Layout()
                
                # Status panel
                status_panel = create_status_panel(controller)
                
                # Telemetry panel
                telemetry = controller.get_telemetry()
                telemetry_panel = create_telemetry_panel(telemetry)
                
                # Combine panels
                layout.split_column(
                    Layout(status_panel, name="status"),
                    Layout(telemetry_panel, name="telemetry")
                )
                
                live.update(layout)
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping dashboard...[/yellow]")


def preset_menu(controller: FVOASController):
    """Interactive preset selection menu."""
    presets = FVOASController.list_presets()
    
    # Categorize presets
    anon_presets = {k: v for k, v in presets.items() 
                   if 'anonymous' in k.lower() or 'dynamic' in k.lower()}
    other_presets = {k: v for k, v in presets.items() 
                    if k not in anon_presets}
    
    console.print("\n[bold cyan]═══ PRESET SELECTION ═══[/bold cyan]\n")
    
    # Show anonymization presets first
    console.print("[bold yellow]Primary Anonymization Presets:[/bold yellow]")
    anon_list = sorted(anon_presets.keys())
    for i, name in enumerate(anon_list, 1):
        desc = anon_presets[name].get('description', '')
        console.print(f"  {i}. [cyan]{name}[/cyan] - {desc[:60]}")
    
    # Show other presets
    if other_presets:
        console.print("\n[bold yellow]Other Presets:[/bold yellow]")
        other_list = sorted(other_presets.keys())
        start_num = len(anon_list) + 1
        for i, name in enumerate(other_list, start_num):
            desc = other_presets[name].get('description', '')
            console.print(f"  {i}. [cyan]{name}[/cyan] - {desc[:60]}")
    
    # Get selection
    all_presets = anon_list + other_list
    try:
        choice = Prompt.ask("\n[bold yellow]Select preset number[/bold yellow]", 
                           default="1")
        idx = int(choice) - 1
        if 0 <= idx < len(all_presets):
            preset_name = all_presets[idx]
            console.print(f"\n[yellow]Applying preset: {preset_name}[/yellow]")
            controller.set_preset(preset_name)
            console.print(f"[green]✓ Preset applied successfully[/green]")
        else:
            console.print("[red]Invalid selection[/red]")
    except (ValueError, KeyboardInterrupt):
        console.print("[yellow]Cancelled[/yellow]")


def custom_parameters_menu(controller: FVOASController):
    """Menu for setting custom parameters."""
    console.print("\n[bold cyan]═══ CUSTOM PARAMETERS ═══[/bold cyan]\n")
    
    try:
        pitch = Prompt.ask("[cyan]Pitch adjustment (semitones)[/cyan]", 
                          default="0.0")
        formant = Prompt.ask("[cyan]Formant ratio[/cyan]", default="1.0")
        
        pitch_val = float(pitch)
        formant_val = float(formant)
        
        console.print(f"\n[yellow]Applying: Pitch={pitch_val:+.2f}, Formant={formant_val:.3f}[/yellow]")
        
        from ..fvoas import ObfuscationParams
        params = ObfuscationParams(
            pitch_semitones=pitch_val,
            formant_ratio=formant_val,
        )
        controller.kernel.set_params(params)
        controller._current_preset = "custom"
        
        console.print("[green]✓ Parameters applied[/green]")
    except (ValueError, KeyboardInterrupt) as e:
        console.print(f"[red]Error: {e}[/red]")


def dynamic_target_menu(controller: FVOASController):
    """Menu for setting dynamic anonymization target."""
    console.print("\n[bold cyan]═══ DYNAMIC ANONYMIZATION TARGET ═══[/bold cyan]\n")
    console.print("1. Neutral (gender-neutral)")
    console.print("2. Male (masculine)")
    console.print("3. Female (feminine)")
    console.print("4. Robot (synthetic)")
    console.print("5. Custom")
    
    try:
        choice = Prompt.ask("\n[bold yellow]Select target[/bold yellow]", 
                          choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            controller.set_preset('dynamic_neutral')
        elif choice == "2":
            controller.set_preset('dynamic_male')
        elif choice == "3":
            controller.set_preset('dynamic_female')
        elif choice == "4":
            controller.set_preset('dynamic_robot')
        elif choice == "5":
            f0 = Prompt.ask("[cyan]Target F0 (Hz)[/cyan]", default="165.0")
            f1 = Prompt.ask("[cyan]Target F1 (Hz)[/cyan]", default="500.0")
            f2 = Prompt.ask("[cyan]Target F2 (Hz)[/cyan]", default="1500.0")
            f3 = Prompt.ask("[cyan]Target F3 (Hz)[/cyan]", default="2500.0")
            
            controller.set_dynamic_target(
                target="custom",
                custom_f0=float(f0),
                custom_formants=(float(f1), float(f2), float(f3))
            )
        
        console.print("[green]✓ Dynamic target set[/green]")
    except (ValueError, KeyboardInterrupt) as e:
        console.print(f"[red]Error: {e}[/red]")


@click.group()
def cli():
    """FVOAS - Federal Voice Obfuscation and Analysis Suite TUI"""
    pass


@cli.command()
def interactive():
    """Interactive TUI mode."""
    print_banner()
    
    try:
        with FVOASController() as controller:
            console.print("[green]✓ FVOAS Controller initialized[/green]\n")
            
            while True:
                console.print("\n[bold cyan]═══ MAIN MENU ═══[/bold cyan]\n")
                console.print("1. Real-Time Dashboard")
                console.print("2. Select Preset")
                console.print("3. Custom Parameters")
                console.print("4. Dynamic Anonymization Target")
                console.print("5. View Presets")
                console.print("6. System Status")
                console.print("7. Exit")
                
                choice = Prompt.ask("\n[bold yellow]Select option[/bold yellow]", 
                                   choices=["1", "2", "3", "4", "5", "6", "7"], 
                                   default="1")
                
                if choice == "1":
                    realtime_dashboard(controller)
                elif choice == "2":
                    preset_menu(controller)
                elif choice == "3":
                    custom_parameters_menu(controller)
                elif choice == "4":
                    dynamic_target_menu(controller)
                elif choice == "5":
                    console.print()
                    console.print(create_presets_table())
                elif choice == "6":
                    console.print()
                    console.print(create_status_panel(controller))
                elif choice == "7":
                    console.print("\n[bold cyan]Shutting down FVOAS...[/bold cyan]\n")
                    break
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


@cli.command()
@click.argument('preset', required=False)
@click.option('--dashboard', '-d', is_flag=True, help='Show real-time dashboard')
def start(preset, dashboard):
    """Start FVOAS with optional preset."""
    print_banner()
    
    try:
        with FVOASController() as controller:
            console.print("[green]✓ FVOAS Controller initialized[/green]\n")
            
            if preset:
                console.print(f"[yellow]Applying preset: {preset}[/yellow]")
                controller.set_preset(preset)
                console.print("[green]✓ Preset applied[/green]\n")
            
            if dashboard:
                realtime_dashboard(controller)
            else:
                console.print("[yellow]FVOAS running. Press Ctrl+C to stop.[/yellow]")
                try:
                    while True:
                        time.sleep(1)
                        stats = controller.get_stats()
                        console.print(f"\r[cyan]Uptime: {stats['uptime_seconds']:.1f}s | "
                                    f"Telemetry: {stats['telemetry_count']} | "
                                    f"Preset: {stats['current_preset']}[/cyan]", 
                                    end="")
                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopping...[/yellow]")
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


@cli.command()
def list_presets():
    """List all available presets."""
    print_banner()
    console.print()
    console.print(create_presets_table())


@cli.command()
def status():
    """Show current FVOAS status."""
    print_banner()
    
    try:
        with FVOASController() as controller:
            console.print()
            console.print(create_status_panel(controller))
            
            telemetry = controller.get_telemetry()
            if telemetry:
                console.print()
                console.print(create_telemetry_panel(telemetry))
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()
