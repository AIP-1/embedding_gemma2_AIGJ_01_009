#!/usr/bin/env bash
# 6단계 측정 표 5행을 한 번에 측정해서 표로 출력 (~/eg2-lab 에서 실행)
cd ~/eg2-lab
source ~/eg2/bin/activate
declare -A NAME=([text]="텍스트 전용" [image]="+비전" [video]="+비전" [audio]="+오디오" [all]="전체")
declare -A SIZE=([text]=270M [image]=440M [video]=440M [audio]=570M [all]=740M)
declare -A INP=([text]="질의 2개" [image]="이미지 5장" [video]="동영상 10초" [audio]="WAV 3개" [all]="혼합")
rows=()
for m in text image video audio all; do
  echo ">> $m 측정 중..." >&2
  r=$(python bench.py "$m" 2>bench_$m.err | grep '^RESULT|') || { echo "   실패: bench_$m.err 확인" >&2; continue; }
  IFS='|' read -r _ _ ram delta peak lat gpu <<< "$r"
  rows+=("| ${NAME[$m]} | ${SIZE[$m]} | $ram (+$delta) | ${INP[$m]} | $lat | $gpu |")
  sleep 3
done
echo
echo "| 구성 | 로드 크기 | 로드 후 RAM (MB) | 입력 | 지연 (ms) | GPU 사용률 (%) |"
echo "|---|---|---|---|---|---|"
printf '%s\n' "${rows[@]}"
echo
echo "RAM: tegrastats 기준 시스템 전체 사용량 (괄호는 모델 로드로 늘어난 양)"
echo "지연: 워밍업 1회 제외, 3회 평균 / GPU: 측정 구간 GR3D_FREQ 최대값"
