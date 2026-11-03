import glob, time
import soundfile as sf
from eg2 import load

model = load(audio=True)   # 텍스트 + 오디오 (570M)

files = sorted(f for f in glob.glob("media/*.wav") if "/raw_" not in f)
waves = []
for f in files:
    info = sf.info(f)
    assert info.samplerate == 16000 and info.channels == 1, f"{f}: 16kHz 모노가 아님"
    w, _ = sf.read(f, dtype="float32")   # torchcodec 없이 직접 읽기
    waves.append(w)

t = time.perf_counter()
aud_emb = model.encode([{"audio": w} for w in waves], normalize_embeddings=True)
print(f"오디오 {len(files)}개: {(time.perf_counter()-t)*1000:.0f} ms")

queries = ["덥다고 냉방을 요청하는 목소리", "날카로운 경보음", "웅웅거리는 배경 소음"]
q = model.encode(queries, prompt_name="SearchQuery", normalize_embeddings=True)

sim = q @ aud_emb.T
for qi, row in zip(queries, sim):
    best = row.argmax()
    print(f"{qi} -> {files[best].split('/')[-1]} ({row[best]:.3f})  | 전체: " +
          ", ".join(f"{f.split('/')[-1]}={s:.3f}" for f, s in zip(files, row)))
