# torchcodec 없이(JetPack 7 + Jetson torch) PyAV로 초당 1프레임을 뽑아 동영상 임베딩
import time, av, numpy as np, torch
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

model = load(vision=True)
queries = ["모니터와 페트병이 놓인 빈 책상", "게 그림이 있는 회색 맨투맨",
           "형광등과 천장 에어컨이 있는 강의실 천장", "강의실에 앉아 있는 학생"]
Q = model.encode(queries, prompt_name="SearchQuery", normalize_embeddings=True)

frames = read_video("media/clip.mp4")
print(f"추출 프레임 {frames.shape}")
t = time.perf_counter()
V = model.encode([{"video": frames}], normalize_embeddings=True)
print(f"\n[동영상 clip.mp4] {(time.perf_counter()-t)*1000:.0f} ms")
for q, s in zip(queries, (Q @ V.T)[:, 0]):
    print(f"  {q}: {s:.3f}")
print(f"\nGPU 메모리 최대 {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
