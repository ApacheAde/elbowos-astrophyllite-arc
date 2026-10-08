# Astrophyllite Arc

Full-colour Python 3 neon bronze asteroid arcade for [ElbowOS](https://x.com/ElbowOS).

A copper dart orbits a starburst crystal. Shatter the drifting mineral shards — big shards split. Not a ROM, not an emulator, original rules and art.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 astrophyllite_arc.py --play
```

A / D rotate, W / S radial thrust, Space fire, R restart.

## Record a 9:16 reel

```bash
python3 astrophyllite_arc.py
```

Headless autoplay writes a 15s 1080x1920 H.264 MP4 (dummy SDL video driver, ffmpeg libx264 yuv420p CRF 20, +faststart).

* Featured account: https://x.com/ElbowOS
* Drive reel: https://drive.google.com/file/d/1pVDWD1w1u4ynQld9qPdbhtyx-4VS1DaE/view
