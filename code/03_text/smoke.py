import torch
from eg2 import load

m = load()  # 텍스트 인코더만 (270M)
s = ["요리사가 손님을 위해 맛있는 음식을 만들었다.",
     "셰프가 방문객에게 근사한 저녁을 대접했다.",
     "오늘 도쿄는 맑다."]
e = m.encode(s, prompt_name="SentenceSimilarity")
print(e.shape)                 # (3, 768)
print(m.similarity(e, e))      # 0-1 쌍이 0-2 쌍보다 높아야 정상
print(f"GPU 메모리 {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
