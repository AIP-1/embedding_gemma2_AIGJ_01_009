# pose_log.csv 요약: 모드별 평균 fps, 평균 RAM, 마지막 동작별 횟수
import csv, collections
rows = collections.defaultdict(list)
for r in csv.reader(open("pose_log.csv", encoding="utf-8")):
    if len(r) != 9: continue
    t, mode, fps, people, a, b, c, d, ram = r
    rows[mode].append((float(fps), int(people), [int(a), int(b), int(c), int(d)], int(ram)))
print(f"{'모드':18} {'fps':>5} {'RAM(MB)':>8}   만세 한팔 손흔들기 악수  (기록 수)")
for m, v in rows.items():
    f = [x[0] for x in v if x[1] > 0] or [x[0] for x in v]   # 사람이 있을 때 fps
    ram = sum(x[3] for x in v) / len(v)
    cnt = v[-1][2]
    print(f"{m:18} {sum(f)/len(f):5.1f} {ram:8.0f}   {cnt[0]:>4} {cnt[1]:>4} {cnt[2]:>6} {cnt[3]:>4}  ({len(v)})")
