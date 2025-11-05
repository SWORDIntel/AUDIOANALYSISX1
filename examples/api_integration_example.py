#!/usr/bin/env python3
"""
API Integration Examples
========================

Demonstrates various ways to integrate with AUDIOANALYSISX1 API.
"""

import asyncio
import time
from pathlib import Path
from audioanalysisx1.api import AudioAnalysisClient


def example_1_basic_analysis():
    """Example 1: Basic file analysis."""
    print("=" * 60)
    print("Example 1: Basic File Analysis")
    print("=" * 60)

    # Initialize client
    client = AudioAnalysisClient("http://localhost:8000")

    # Check server health
    health = client.health_check()
    print(f"Server status: {health['status']}")
    print(f"Server version: {health['version']}")

    # Analyze a file
    print("\nSubmitting analysis job...")
    job = client.analyze_file(
        "sample_audio.wav",
        asset_id="example_001",
        save_visualizations=True
    )
    print(f"Job ID: {job['job_id']}")

    # Wait for result
    print("Waiting for analysis to complete...")
    result = client.wait_for_result(job['job_id'], timeout=120)

    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Alteration Detected: {result.get('ALTERATION_DETECTED')}")
    print(f"Confidence: {result.get('CONFIDENCE')}")
    print(f"Presented As: {result.get('PRESENTED_AS')}")
    print(f"Probable Sex: {result.get('PROBABLE_SEX')}")
    print()


def example_2_async_with_webhook():
    """Example 2: Async analysis with webhook."""
    print("=" * 60)
    print("Example 2: Async Analysis with Webhook")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # Submit job with webhook
    job = client.analyze_file(
        "sample_audio.wav",
        asset_id="example_002",
        webhook_url="https://webhook.site/your-webhook-id"
    )

    print(f"Job submitted: {job['job_id']}")
    print("Your webhook will receive the results when complete.")
    print()


def example_3_batch_processing():
    """Example 3: Batch processing multiple files."""
    print("=" * 60)
    print("Example 3: Batch Processing")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # List of files to process
    files = [
        "audio1.wav",
        "audio2.wav",
        "audio3.wav"
    ]

    # Submit batch
    print(f"Submitting batch of {len(files)} files...")
    batch = client.batch_analyze(
        files,
        asset_ids=[f"batch_{i}" for i in range(len(files))],
        save_visualizations=True
    )

    print(f"Batch ID: {batch['batch_id']}")
    print(f"Job IDs: {batch['job_ids']}")

    # Wait for all jobs
    print("\nWaiting for all jobs to complete...")
    results = []
    for job_id in batch['job_ids']:
        try:
            result = client.wait_for_result(job_id, timeout=120)
            results.append(result)
            print(f"✓ Job {job_id} completed")
        except Exception as e:
            print(f"✗ Job {job_id} failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("BATCH RESULTS SUMMARY")
    print("=" * 60)
    total = len(results)
    altered = sum(1 for r in results if r.get('ALTERATION_DETECTED'))
    print(f"Total analyzed: {total}")
    print(f"Alterations detected: {altered}")
    print(f"Clean audio: {total - altered}")
    print()


def example_4_url_analysis():
    """Example 4: Analyze audio from URL."""
    print("=" * 60)
    print("Example 4: URL Analysis")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # Analyze from URL
    job = client.analyze_url(
        "https://example.com/audio.wav",
        asset_id="url_example"
    )

    print(f"Job submitted: {job['job_id']}")
    result = client.wait_for_result(job['job_id'])

    print(f"Analysis complete: {result.get('ALTERATION_DETECTED')}")
    print()


def example_5_get_visualizations():
    """Example 5: Download visualizations."""
    print("=" * 60)
    print("Example 5: Download Visualizations")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # Analyze file
    job = client.analyze_file("sample_audio.wav")
    result = client.wait_for_result(job['job_id'])

    # Download visualizations
    plot_names = ['overview', 'spectrogram', 'phase_coherence', 'pitch_formant']

    output_dir = Path("visualizations")
    output_dir.mkdir(exist_ok=True)

    print("\nDownloading visualizations...")
    for plot_name in plot_names:
        try:
            save_path = output_dir / f"{job['job_id']}_{plot_name}.png"
            client.get_visualization(job['job_id'], plot_name, str(save_path))
            print(f"✓ Downloaded {plot_name}")
        except Exception as e:
            print(f"✗ Failed to download {plot_name}: {e}")

    print(f"\nVisualizations saved to: {output_dir}")
    print()


def example_6_list_and_manage_jobs():
    """Example 6: List and manage jobs."""
    print("=" * 60)
    print("Example 6: Job Management")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # Get statistics
    stats = client.get_stats()
    print("Server Statistics:")
    print(f"  Total processed: {stats['total_processed']}")
    print(f"  Total failed: {stats['total_failed']}")
    print(f"  Active jobs: {stats['active_jobs']}")

    # List recent jobs
    print("\nRecent Jobs:")
    jobs = client.list_jobs(limit=5)
    for job in jobs:
        print(f"  {job['job_id']}: {job['status']} (created: {job['created_at']})")

    # List only completed jobs
    print("\nCompleted Jobs:")
    completed_jobs = client.list_jobs(status='completed', limit=5)
    for job in completed_jobs:
        print(f"  {job['job_id']}")

    print()


async def example_7_streaming():
    """Example 7: Real-time streaming analysis."""
    print("=" * 60)
    print("Example 7: Streaming Analysis")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # Read audio file
    audio_path = Path("sample_audio.wav")
    if not audio_path.exists():
        print("Sample audio file not found, skipping streaming example")
        return

    audio_data = audio_path.read_bytes()

    # Split into chunks (simulate streaming)
    chunk_size = 8192  # 8KB chunks
    chunks = [
        audio_data[i:i+chunk_size]
        for i in range(0, len(audio_data), chunk_size)
    ]

    print(f"Streaming {len(chunks)} chunks...")

    async with client.stream() as stream:
        # Send chunks
        for i, chunk in enumerate(chunks):
            is_final = (i == len(chunks) - 1)
            response = await stream.send_chunk(chunk, is_final=is_final)

            if 'progress' in response:
                print(f"Progress: {response['progress']:.1%}")

        # Get final result
        result = await stream.get_result()

        print("\n" + "=" * 60)
        print("STREAMING ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Alteration Detected: {result.get('ALTERATION_DETECTED')}")
        print(f"Confidence: {result.get('CONFIDENCE')}")
        print()


def example_8_error_handling():
    """Example 8: Error handling."""
    print("=" * 60)
    print("Example 8: Error Handling")
    print("=" * 60)

    client = AudioAnalysisClient("http://localhost:8000")

    # Try to get non-existent job
    try:
        job = client.get_job("non_existent_job_id")
    except Exception as e:
        print(f"Expected error caught: {e}")

    # Try with invalid file
    try:
        job = client.analyze_file("non_existent_file.wav")
    except Exception as e:
        print(f"Expected error caught: {e}")

    # Cancel a job
    print("\nSubmitting and cancelling a job...")
    job = client.analyze_file("sample_audio.wav")
    time.sleep(0.5)  # Give it a moment to start

    try:
        client.cancel_job(job['job_id'])
        print(f"Job {job['job_id']} cancelled successfully")
    except Exception as e:
        print(f"Could not cancel job: {e}")

    print()


def main():
    """Run all examples."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     AUDIOANALYSISX1 API Integration Examples                 ║
╚══════════════════════════════════════════════════════════════╝

Make sure the API server is running:
    python run_api_server.py

Then run these examples to learn how to integrate the API.
""")

    # Run synchronous examples
    try:
        example_1_basic_analysis()
    except Exception as e:
        print(f"Example 1 error: {e}\n")

    try:
        example_2_async_with_webhook()
    except Exception as e:
        print(f"Example 2 error: {e}\n")

    try:
        example_3_batch_processing()
    except Exception as e:
        print(f"Example 3 error: {e}\n")

    try:
        example_4_url_analysis()
    except Exception as e:
        print(f"Example 4 error: {e}\n")

    try:
        example_5_get_visualizations()
    except Exception as e:
        print(f"Example 5 error: {e}\n")

    try:
        example_6_list_and_manage_jobs()
    except Exception as e:
        print(f"Example 6 error: {e}\n")

    # Run async example
    try:
        asyncio.run(example_7_streaming())
    except Exception as e:
        print(f"Example 7 error: {e}\n")

    try:
        example_8_error_handling()
    except Exception as e:
        print(f"Example 8 error: {e}\n")

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
