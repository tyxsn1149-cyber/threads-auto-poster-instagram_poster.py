"""Render the three approved stills with an original soft music-box bed."""
from pathlib import Path
import hashlib, json, math, shutil, subprocess, wave
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'generated_images'
NAMES = ['exec-97726798-9158-4045-b5f1-ae5517c2c893.png', 'exec-95e609fb-a1f5-4a36-9d0d-3603acc59fb3.png', 'exec-ebab468d-e13d-45ea-83c1-f2e91fb87b17.png']
for i, name in enumerate(NAMES, 1):
    if not (ROOT / f'slide-{i}.png').exists():
        shutil.copyfile(SOURCE / name, ROOT / f'slide-{i}.png')

rate, seconds = 44100, 18
audio = np.zeros(rate * seconds, dtype=np.float64)
# Original sparse arpeggio; no sampled or licensed music, no narration.
notes = [72, 76, 79, 76, 69, 72, 76, 72, 65, 69, 72, 69, 67, 71, 74, 71]
for k in range(23):
    onset = 0.35 + k * 0.75
    start = int(onset * rate)
    count = min(int(2.8 * rate), len(audio) - start)
    if count <= 0:
        break
    t = np.arange(count) / rate
    frequency = 440 * 2 ** ((notes[k % len(notes)] - 69) / 12)
    envelope = (1 - np.exp(-t * 90)) * np.exp(-t * 2.1)
    tone = (np.sin(2 * np.pi * frequency * t)
            + .24 * np.sin(2 * np.pi * frequency * 2.76 * t) * np.exp(-t * 3)
            + .10 * np.sin(2 * np.pi * frequency * 5.4 * t) * np.exp(-t * 5))
    audio[start:start + count] += .09 * envelope * tone
audio *= np.minimum(np.arange(len(audio)) / rate / .5, 1)
audio *= np.minimum((len(audio) - np.arange(len(audio))) / rate / 1.5, 1)
with wave.open(str(ROOT / 'music-box.wav'), 'wb') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(np.repeat((audio * 32767).astype('<i2')[:, None], 2, axis=1).tobytes())

cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-filter_complex_threads', '1']
for i, duration in enumerate([4.5, 7.5, 7], 1):
    cmd += ['-loop', '1', '-framerate', '30', '-t', str(duration), '-i', str(ROOT / f'slide-{i}.png')]
cmd += ['-i', str(ROOT / 'music-box.wav')]
filters = []
for i in range(3):
    filters.append(f'[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0xfaf7ef,setsar=1,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]')
filters += ['[v0][v1]xfade=transition=slideup:duration=0.5:offset=4[v01]',
            '[v01][v2]xfade=transition=slideup:duration=0.5:offset=11[vout]']
cmd += ['-filter_complex', ';'.join(filters), '-map', '[vout]', '-map', '3:a',
        '-t', '18', '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '27',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-ar', '44100',
        '-movflags', '+faststart', '-threads', '2', str(ROOT / 'ig052-reel-18s.mp4')]
subprocess.run(cmd, check=True)
files = {}
for path in [*(ROOT / f'slide-{i}.png' for i in range(1, 4)), ROOT / 'music-box.wav', ROOT / 'ig052-reel-18s.mp4']:
    data = path.read_bytes()
    files[path.name] = {'size': len(data), 'git_blob_sha': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}
(ROOT / 'manifest.json').write_text(json.dumps(files, indent=2) + '\n')
print(json.dumps(files))

