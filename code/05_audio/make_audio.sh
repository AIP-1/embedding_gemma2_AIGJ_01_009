#!/usr/bin/env bash
# Jetson ~/eg2-lab 에서 실행: 경보음·잡음 생성 + 모든 raw_* 를 16kHz 모노 wav로 변환
cd ~/eg2-lab
ffmpeg -y -loglevel error -f lavfi -i "sine=frequency=1000:duration=3" media/raw_beep.wav
ffmpeg -y -loglevel error -f lavfi -i "anoisesrc=color=pink:duration=5" media/raw_noise.wav
for f in media/raw_*.wav media/raw_*.m4a media/raw_*.aiff; do
  [ -e "$f" ] || continue
  out="media/$(basename "${f%.*}" | sed 's/^raw_//').wav"
  ffmpeg -y -loglevel error -i "$f" -ar 16000 -ac 1 "$out" && echo "변환: $out"
done
python - <<'PY'
import glob, soundfile as sf
for f in sorted(glob.glob("media/*.wav")):
    if "/raw_" in f: continue
    i = sf.info(f); print(f, i.samplerate, "Hz", i.channels, "ch", f"{i.duration:.1f}s")
PY
