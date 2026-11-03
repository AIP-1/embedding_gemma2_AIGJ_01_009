# 6단계 측정 표 자동 측정: python bench.py <text|image|video|audio|all>
# 구성마다 새 프로세스로 실행해야 RAM이 정확함 → run_bench.sh 사용
import sys, glob, re, time, threading, subprocess
import av, numpy as np, soundfile as sf, torch
from eg2 import load

MODE = sys.argv[1]

# ---- tegrastats를 100ms 간격으로 읽어 RAM·GPU 사용률 기록 ----
samples = []  # (시각, RAM MB, GPU %)
def _reader():
    p = subprocess.Popen(["tegrastats", "--interval", "100"], stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        ram = re.search(r"RAM (\d+)/", line); gpu = re.search(r"GR3D_FREQ (\d+)%", line)
        if ram: samples.append((time.time(), int(ram.group(1)), int(gpu.group(1)) if gpu else 0))
threading.Thread(target=_reader, daemon=True).start()
def ram_now():
    time.sleep(0.5); return samples[-1][1] if samples else -1
def gpu_max(t0, t1):
    v = [g for t, _, g in samples if t0 <= t <= t1]; return max(v) if v else -1

def read_video(path, fps=1, max_frames=58):
    c = av.open(path); s = c.streams.video[0]; frames, nxt = [], 0.0
    for f in c.decode(s):
        if f.pts is None: continue
        if float(f.pts * s.time_base) >= nxt:
            frames.append(f.to_ndarray(format="rgb24")); nxt += 1.0 / fps
            if len(frames) >= max_frames: break
    c.close(); return np.stack(frames)

def wavs():
    out = []
    for p in sorted(f for f in glob.glob("media/*.wav") if "/raw_" not in f):
        w, sr = sf.read(p, dtype="float32"); assert sr == 16000 and w.ndim == 1, p
        out.append({"audio": w})
    return out

time.sleep(1.5); base = ram_now()
cfg = {"text": dict(), "image": dict(vision=True), "video": dict(vision=True),
       "audio": dict(audio=True), "all": dict(vision=True, audio=True)}[MODE]
model = load(**cfg); torch.cuda.synchronize()
loaded = ram_now()

queries = ["수업 중에 졸리고 머리가 맑지 않아요", "여름에 냉방 몇 도로 맞춰야 하나요?"]
imgs = [{"image": p} for p in sorted(glob.glob("media/*.jpg"))]
if MODE == "text":
    run = lambda: model.encode(queries, prompt_name="SearchQuery")
elif MODE == "image":
    run = lambda: model.encode(imgs)
elif MODE == "video":
    vid = [{"video": read_video("media/clip.mp4")}]
    run = lambda: model.encode(vid)
elif MODE == "audio":
    aud = wavs(); run = lambda: model.encode(aud)
else:  # 혼합: 이미지 5 + 동영상 1 + 음성 3 + 질의 2
    mix = imgs + [{"video": read_video("media/clip.mp4")}] + wavs()
    run = lambda: (model.encode(mix), model.encode(queries, prompt_name="SearchQuery"))

run(); torch.cuda.synchronize()                    # 1회차: 워밍업 (기록 안 함)
lat = []
t0 = time.time()
for _ in range(3):                                 # 2~4회차 평균
    t = time.perf_counter(); run(); torch.cuda.synchronize()
    lat.append((time.perf_counter() - t) * 1000)
t1 = time.time(); time.sleep(0.3)
peak = max(r for t, r, _ in samples if t0 <= t <= t1 + 0.3)

print(f"RESULT|{MODE}|{loaded}|{loaded-base}|{peak}|{np.mean(lat):.0f}|{gpu_max(t0, t1)}")
