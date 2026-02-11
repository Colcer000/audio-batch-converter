import subprocess
import re

def analyze_replaygain(file_path: str):
    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-filter:a", "ebur128=peak=true",
        "-f", "null",
        "-"
    ]
    result = subprocess.run(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    stderr = result.stderr

    # Integrated loudness
    loudness_match = re.search(r"Integrated loudness:\s+I:\s*(-?\d+\.?\d*) LUFS", stderr)
    # True peak
    peak_match = re.search(r"Peak:\s*(-?\d+\.?\d*) dBFS", stderr)

    if not loudness_match or not peak_match:
        return None

    loudness = float(loudness_match.group(1))
    peak = float(peak_match.group(1))

    # ReplayGain reference is -18 LUFS
    gain = -18.0 - loudness

    print(f"Loudness: {loudness}, Peak: {peak}, Gain: {gain}")

    return round(gain, 2), round(peak, 2)
