#!/usr/bin/env python3
"""
Voice Modifier - Real-time Voice Transformation
================================================

Simple CLI interface for real-time voice modification.

Usage:
    python run_voice_modifier.py                    # Default settings
    python run_voice_modifier.py --preset robot     # Use preset
    python run_voice_modifier.py --list-devices     # List audio devices
    python run_voice_modifier.py --list-presets     # List available presets
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audioanalysisx1.voicemod import VoiceModifier, AudioProcessor, PRESET_LIBRARY, ETHICAL_NOTICE
from audioanalysisx1.voicemod.realtime import AudioConfig


def list_devices(modifier: VoiceModifier):
    """List available audio devices."""
    devices = modifier.list_devices()

    print("\n" + "="*60)
    print("AVAILABLE AUDIO DEVICES")
    print("="*60)

    print("\nInput Devices:")
    for dev in devices['input']:
        print(f"  [{dev['index']}] {dev['name']}")
        print(f"      Channels: {dev['channels']}, Sample Rate: {dev['sample_rate']:.0f}Hz")

    print("\nOutput Devices:")
    for dev in devices['output']:
        print(f"  [{dev['index']}] {dev['name']}")
        print(f"      Channels: {dev['channels']}, Sample Rate: {dev['sample_rate']:.0f}Hz")

    print()


def list_presets():
    """List available presets."""
    print("\n" + "="*60)
    print("AVAILABLE VOICE PRESETS")
    print("="*60)

    categories = {
        'Gender Transformation': ['male_to_female', 'female_to_male',
                                 'male_to_female_subtle', 'female_to_male_subtle'],
        'Character Voices': ['chipmunk', 'giant', 'robot', 'demon', 'alien'],
        'Utility Effects': ['whisper', 'megaphone', 'telephone', 'cave'],
        'Anonymization': ['anonymous_1', 'anonymous_2', 'anonymous_3'],
    }

    for category, preset_names in categories.items():
        print(f"\n{category}:")
        for name in preset_names:
            if name in PRESET_LIBRARY:
                preset = PRESET_LIBRARY[name]
                print(f"  {name:25} - {preset.description}")

    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Real-time Voice Modifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=ETHICAL_NOTICE
    )

    parser.add_argument(
        '--preset',
        type=str,
        help='Voice preset to use (e.g., male_to_female, robot, anonymous_1)'
    )

    parser.add_argument(
        '--pitch',
        type=float,
        help='Pitch shift in semitones (overrides preset)'
    )

    parser.add_argument(
        '--formant',
        type=float,
        help='Formant shift ratio (overrides preset)'
    )

    parser.add_argument(
        '--input-device',
        type=int,
        help='Input device index'
    )

    parser.add_argument(
        '--output-device',
        type=int,
        help='Output device index'
    )

    parser.add_argument(
        '--sample-rate',
        type=int,
        default=48000,
        help='Sample rate in Hz (default: 48000)'
    )

    parser.add_argument(
        '--block-size',
        type=int,
        default=2048,
        help='Block size in samples (default: 2048)'
    )

    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available audio devices and exit'
    )

    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List available presets and exit'
    )

    parser.add_argument(
        '--bypass',
        action='store_true',
        help='Start in bypass mode (no processing)'
    )

    args = parser.parse_args()

    # Show ethical notice
    print(ETHICAL_NOTICE)

    # List presets if requested
    if args.list_presets:
        list_presets()
        return

    # Create audio config
    config = AudioConfig(
        sample_rate=args.sample_rate,
        block_size=args.block_size
    )

    # Create voice modifier
    modifier = VoiceModifier(config)

    # List devices if requested
    if args.list_devices:
        list_devices(modifier)
        return

    # Set devices
    if args.input_device is not None or args.output_device is not None:
        modifier.set_devices(args.input_device, args.output_device)

    # Create processor
    processor = AudioProcessor()

    # Apply preset if specified
    if args.preset:
        if args.preset in PRESET_LIBRARY:
            processor.apply_preset_by_name(args.preset)
            print(f"\n✓ Applied preset: {args.preset}")
        else:
            print(f"\n✗ Unknown preset: {args.preset}")
            print("   Use --list-presets to see available presets")
            return

    # Override with command-line arguments
    if args.pitch is not None:
        processor.set_pitch(args.pitch)
        print(f"✓ Pitch: {args.pitch:+.1f} semitones")

    if args.formant is not None:
        processor.set_formant(args.formant)
        print(f"✓ Formant ratio: {args.formant:.2f}")

    # Set bypass mode
    if args.bypass:
        processor.set_bypass(True)
        print("✓ Bypass mode enabled")

    # Add processor to modifier
    modifier.add_effect(processor)

    # Show configuration
    print("\n" + "="*60)
    print("VOICE MODIFIER CONFIGURATION")
    print("="*60)
    print(f"Sample Rate:    {config.sample_rate} Hz")
    print(f"Block Size:     {config.block_size} samples")
    print(f"Latency:        ~{config.latency_ms:.1f} ms")

    settings = processor.get_settings()
    print(f"\nCurrent Settings:")
    print(f"  Pitch:        {settings['pitch_semitones']:+.1f} semitones")
    print(f"  Formant:      {settings['formant_ratio']:.2f}x")
    print(f"  Time Stretch: {settings['time_stretch_rate']:.2f}x")
    print(f"  Reverb:       {settings['reverb_wet']:.2f}")
    print(f"  Echo:         {settings['echo_wet']:.2f}")
    print(f"  Noise Gate:   {'Enabled' if settings['use_noise_gate'] else 'Disabled'}")
    print(f"  Compression:  {'Enabled' if settings['use_compression'] else 'Disabled'}")
    print(f"  Bypass:       {'Enabled' if settings['bypass'] else 'Disabled'}")

    print("\n" + "="*60)
    print("STARTING VOICE MODIFICATION")
    print("="*60)
    print("\nPress Ctrl+C to stop.\n")

    # Start voice modification
    try:
        modifier.start()

        # Main loop - just keep running and show stats
        import time
        while True:
            time.sleep(1)

            # Show stats every second
            stats = modifier.get_stats()
            levels = modifier.get_levels()

            # Simple level meters
            input_bar = '█' * int(levels['input'] * 50)
            output_bar = '█' * int(levels['output'] * 50)

            print(f"\rInput:  [{input_bar:<50}] | Output: [{output_bar:<50}] | "
                  f"Process: {stats['process_time_ms']:.1f}ms | "
                  f"Underruns: {stats['buffer_underruns']}", end='', flush=True)

    except KeyboardInterrupt:
        print("\n\nStopping voice modifier...")
        modifier.stop()
        print("Voice modifier stopped.")

    except Exception as e:
        print(f"\n\nError: {e}", file=sys.stderr)
        modifier.stop()
        sys.exit(1)


if __name__ == '__main__':
    main()
