#!/usr/bin/env bash
# pose_app.py가 켜져 있는 동안 5초마다 모드, fps, 인원, RAM, 동작별 횟수를 pose_log.csv에 기록
# 멈추면(Ctrl+C) 마지막 동작 기록(최근 20개)을 pose_events_<모드>.txt로 저장
# 사용법: bash log_pose.sh
cd ~/eg2-lab
last=""
save_events() {
  if [ -n "$last" ]; then
    m=$(echo "$last" | python3 -c "import sys,json; print(json.load(sys.stdin)['mode'].replace(' ','').replace('+','_'))")
    echo "$last" | python3 -c "
import sys, json, time
r = json.load(sys.stdin)
print('모드:', r['mode'])
print('동작별 횟수:', r['counts'])
if r.get('beh'): print('관심도 통계:', r['beh'], ' 관심 비율:', r.get('interest_rate'))
print('--- 동작 기록 (최근 20개, 최신이 위) ---')
for e in r['events']:
    print(time.strftime('%H:%M:%S', time.localtime(e['ts'])), e['who'], e['label'])
" > "pose_events_$m.txt"
    echo; echo "저장: pose_events_$m.txt"
  fi
  exit 0
}
trap save_events INT
while true; do
  j=$(curl -s --max-time 3 localhost:8000/events)
  if [ -z "$j" ]; then
    echo "$(date +%H:%M:%S)  앱 응답 없음 → 다른 창에서 python pose_app.py ... 가 켜져 있는지 확인"
    sleep 5; continue
  fi
  last="$j"
  s=$(echo "$j" | python3 -c "
import sys, json
r = json.load(sys.stdin)
c = r['counts']
print(f\"{r['mode']},{r['stats']['fps']:.1f},{r['stats']['people']},\" +
      ','.join(str(c.get(k, 0)) for k in ['만세', '한팔들기', '손흔들기', '악수']))")
  ram=$(tegrastats --interval 1000 | head -1 | grep -o "RAM [0-9]*" | cut -d' ' -f2)
  echo "$(date +%H:%M:%S),$s,$ram" | tee -a pose_log.csv
  sleep 5
done
