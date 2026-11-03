#!/usr/bin/env bash
# app.py가 켜져 있는 동안 5초마다 모드, fps, 임베딩 ms, RAM을 stats_log.csv에 기록
# 사용법: bash log_stats.sh   (멈출 때 Ctrl+C)
cd ~/eg2-lab
while true; do
  j=$(curl -s --max-time 3 localhost:8000/recent)
  if [ -z "$j" ]; then
    echo "$(date +%H:%M:%S)  앱 응답 없음 → 다른 창에서 python app.py --mode ... 가 켜져 있는지 확인"
    sleep 5; continue
  fi
  s=$(echo "$j" | python3 -c "import sys,json; r=json.load(sys.stdin); s=r['stats']; print(f\"{r['mode']},{s['fps']:.1f},{s['embed_ms']:.0f}\")")
  ram=$(tegrastats --interval 1000 | head -1 | grep -o "RAM [0-9]*" | cut -d' ' -f2)
  echo "$(date +%H:%M:%S),$s,$ram" | tee -a stats_log.csv
  sleep 5
done
