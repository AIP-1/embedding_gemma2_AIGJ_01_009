# stats_log.csv의 모드별 평균 (임베딩 ms가 0인 줄은 제외)
import csv, collections
d = collections.defaultdict(list)
for row in csv.reader(open("stats_log.csv")):
    if len(row) != 5 or not row[1]: continue
    t, m, f, e, r = row
    if float(e) > 0: d[m].append((float(f), float(e), int(r)))
print("모드      fps   임베딩ms  RAM(MB)  (기록 수)")
for m, v in d.items():
    a = [sum(x[i] for x in v) / len(v) for i in range(3)]
    print(f"{m:8} {a[0]:5.1f}  {a[1]:7.0f}  {a[2]:7.0f}   ({len(v)})")
