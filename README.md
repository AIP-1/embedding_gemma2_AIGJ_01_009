
# EmbeddingGemma 2 멀티모달 임베딩 실습 — 단계 1~10 기록

Jetson Orin Nano Super 8GB에서 [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2)로 텍스트·이미지·동영상·음성을 임베딩하고, 웹캠 물체 검색, 사람 동작 인식, 카메라 2대 접근 감지까지 진행한 과제 기록입니다.

- 학번: AIGJ_01_009 (박서현)
- 환경: Python 3.12, torch 2.14.1+cu132, transformers 5.20.1, sentence-transformers 6.2.0, Logitech C920

> 5·6·7단계, 9-6, 10-8의 측정 결과는 아직 채우지 않았습니다. 코드는 들어 있고 결과는 추후 추가합니다.

## 단계 요약

| 단계 | 내용 | 주요 결과 |
|---|---|---|
| 1~2 | 환경 준비, 설치 | 3계정 공유 구성, `torch cuda True`, 모델 로드 `(768,)` |
| 3 | 텍스트 임베딩 | 768/256/128차원 모두 정답 1위, 지연 약 176ms. prompt_name 제거 시 1문항 오답 |
| 4 | 이미지·동영상 | 이미지 질의 4/4 정답. 동영상은 PyAV 프레임 추출로 대체, 가장 오래 나온 장면이 1위 |
| 5 | 오디오 | 샘플 생성·검색 스크립트 (결과 추후) |
| 6 | 성능 측정 | 구성별 측정 스크립트 (결과 추후) |
| 7 | 도메인 미세 조정 | 학습 282쌍·평가 60쌍 데이터, 학습·평가 스크립트 (결과 추후) |
| 8 | 웹캠 물체 검색 | COCO 밖 물체 정답: yolo 0/3 → relabel 1/3(+세탁기 부분) → yoloe 2/3. fps 12.1 → 10.8 → 10.0 |
| 9 | 사람 동작 인식 | 손흔들기 raw 0회 → 개선 1회 인식, 한팔들기 과대 계수(3회) 해소. 행동 패턴 4종 중 머무름만 오판 |
| 10 | 카메라 2대 접근 감지 (지원 님과 함께) | 렌즈 보정 RMS 0.215 / 0.291px, 삼각측량 오차 대부분 10cm 이하, "chair" 타겟 위치 오차 3cm. 한 카메라 추정은 카메라 높이 문제로 미동작 |

전체 내용은 [통합 보고서](report/단계1-10_통합보고서.md) (Word: `report/단계1-10_통합보고서.docx`)에 있습니다.

## 폴더

```
report/    통합 보고서 (md, docx)
code/      단계별 코드 (01_02_setup ~ 10_proximity)
```

## 다시 돌리기

Jetson에서 `code/01_02_setup/system_setup.sh`(관리자 1회)와 `user_setup.sh`(계정마다 1회)를 실행한 뒤, 각 단계 폴더의 스크립트를 `~/eg2-lab`에 두고 실행합니다.

```bash
eg2                                         # venv 활성화 + ~/eg2-lab 이동
python test_text.py                         # 3단계
python test_vision.py && python test_video.py   # 4단계 (media/에 이미지와 clip.mp4 필요)
bash make_audio.sh && python test_audio.py      # 5단계
bash run_bench.sh                           # 6단계
python eval_ir.py && python train_ft.py     # 7단계
python app.py --mode yolo|relabel|yoloe     # 8단계 (브라우저 http://<Jetson IP>:8000)
python pose_app.py --raw / (기본) / --behavior   # 9단계
python proximity_app.py --cams 0 2 --mode ankle1|stereo|fused   # 10단계 (보정 후)
```

