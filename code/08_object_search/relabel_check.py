# crops/<폴더>의 크롭마다 app.py relabel과 같은 방식으로 라벨을 다시 붙여 표로 출력
# 사용법: python relabel_check.py crops/relabel   (결과는 relabel_result.csv에도 저장)
import sys, glob, os, csv, numpy as np, torch
from sentence_transformers import SentenceTransformer

folder = sys.argv[1] if len(sys.argv) > 1 else "crops/relabel"
DIM, LABEL_MIN = 512, 0.20
LABELS = [
    ("drum washing machine", "드럼 세탁기"), ("top-load washing machine", "통돌이 세탁기"),
    ("oven", "오븐"), ("microwave", "전자레인지"), ("refrigerator", "냉장고"),
    ("cell phone", "휴대폰"), ("battery pack", "원통형 전지 포장"), ("AA battery", "건전지"),
    ("laptop", "노트북"), ("monitor", "모니터"), ("keyboard", "키보드"), ("mouse", "마우스"),
    ("cup", "컵"), ("water bottle", "물병"), ("book", "책"), ("backpack", "가방"), ("chair", "의자"),
]
emb = SentenceTransformer("google/embeddinggemma-2", device="cuda",
        model_kwargs={"torch_dtype": torch.bfloat16}, config_kwargs={"audio_config": None})
with torch.inference_mode():
    L = np.asarray(emb.encode([f"a photo of a {en}" for en, _ in LABELS], prompt_name="SearchQuery",
                              truncate_dim=DIM, normalize_embeddings=True), dtype=np.float32)
    files = sorted(glob.glob(f"{folder}/*.jpg"))
    V = np.asarray(emb.encode([{"image": f} for f in files], truncate_dim=DIM,
                              normalize_embeddings=True, batch_size=8), dtype=np.float32)
S = V @ L.T
rows = []
print(f"{'파일':32} {'YOLO':12} → {'재라벨':14} 점수   2위")
for f, s in zip(files, S):
    yolo = os.path.basename(f)[7:-4]
    o = s.argsort()[::-1]; j = o[0]
    en, ko = (LABELS[j] if s[j] >= LABEL_MIN else (yolo, yolo))
    second = f"{LABELS[o[1]][1]}({s[o[1]]:.3f})"
    mark = "*" if en != yolo else " "   # 영어 라벨 기준으로 바뀌었는지 비교
    print(f"{os.path.basename(f):32} {yolo:12} →{mark}{ko:14} {s[j]:.3f}  {second}")
    rows.append([os.path.basename(f), yolo, ko, f"{s[j]:.3f}", second])
with open("relabel_result.csv", "w", newline="", encoding="utf-8-sig") as fp:
    csv.writer(fp).writerows([["file", "yolo", "relabel", "score", "2nd"]] + rows)
print("\n* = YOLO 이름이 바뀐 것 / relabel_result.csv 저장")
