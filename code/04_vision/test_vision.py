import glob, os, time, torch
from eg2 import load

model = load(vision=True)   # 텍스트 + 비전 (440M)

queries = ["모니터와 페트병이 놓인 빈 책상",
           "게 그림이 있는 회색 맨투맨",
           "형광등과 천장 에어컨이 있는 강의실 천장",
           "강의실에 앉아 있는 학생"]
Q = model.encode(queries, prompt_name="SearchQuery", normalize_embeddings=True)

imgs = sorted(glob.glob("media/*.jpg"))
t = time.perf_counter()
E = model.encode([{"image": p} for p in imgs], normalize_embeddings=True)
print(f"\n[이미지 {len(imgs)}장] {(time.perf_counter()-t)*1000:.0f} ms")
sim = Q @ E.T
for q, row in zip(queries, sim):
    top = row.argsort()[::-1][:3]
    print(f"  {q} -> " + ", ".join(f"{os.path.basename(imgs[i])}({row[i]:.3f})" for i in top))
print(f"\nGPU 메모리 최대 {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
