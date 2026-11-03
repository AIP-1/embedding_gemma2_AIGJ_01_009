# 확장 과제: 전체 모델(740M)로 이미지·영상·음성을 한 인덱스에 넣고 하나의 질의로 검색
import glob, os, time, av, numpy as np, soundfile as sf, torch
from eg2 import load

def read_video(path, fps=1, max_frames=58):
    c = av.open(path); s = c.streams.video[0]
    frames, nxt = [], 0.0
    for f in c.decode(s):
        if f.pts is None: continue
        if float(f.pts * s.time_base) >= nxt:
            frames.append(f.to_ndarray(format="rgb24")); nxt += 1.0 / fps
            if len(frames) >= max_frames: break
    c.close()
    return np.stack(frames)

t0 = time.perf_counter()
model = load(vision=True, audio=True)
print(f"전체 모델 로드: {time.perf_counter()-t0:.1f} s")

# 인덱스: (이름, 종류, 입력)
items = []
for p in sorted(glob.glob("media/*.jpg")):
    items.append((os.path.basename(p), "이미지", {"image": p}))
if os.path.exists("media/clip.mp4"):
    items.append(("clip.mp4", "영상", {"video": read_video("media/clip.mp4")}))
for p in sorted(f for f in glob.glob("media/*.wav") if "/raw_" not in f):
    w, sr = sf.read(p, dtype="float32")
    assert sr == 16000 and w.ndim == 1, f"{p}: 16kHz 모노가 아님"
    items.append((os.path.basename(p), "음성", {"audio": w}))

t = time.perf_counter()
index = np.concatenate([model.encode([x], normalize_embeddings=True) for _, _, x in items])
print(f"인덱스 {len(items)}개 임베딩: {(time.perf_counter()-t)*1000:.0f} ms\n")

queries = ["덥다고 냉방을 요청하는 목소리", "날카로운 경보음",
           "모니터와 페트병이 놓인 빈 책상", "강의실에 앉아 있는 학생",
           "에어컨"]
Q = model.encode(queries, prompt_name="SearchQuery", normalize_embeddings=True)
for q, row in zip(queries, Q @ index.T):
    top = row.argsort()[::-1][:3]
    print(f"{q}")
    for r, i in enumerate(top, 1):
        name, kind, _ = items[i]
        print(f"   {r}. [{kind}] {name} ({row[i]:.3f})")

print(f"\nGPU 메모리 최대 {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
