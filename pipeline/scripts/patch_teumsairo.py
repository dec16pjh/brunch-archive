# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(__file__)
path = os.path.join(base, "full_data", "teumsairo2001.json")
d = json.load(open(path, encoding="utf-8"))

poem1 = "머리가 허연 시인이\n머리가 까만 시인들을 모아놓고\n하양에서 까망으로 퍼져가는\n까망에서 하양으로 몰려드는\n시를 이야기한다."
poem2 = "내 시를 이야기하지 마라\n내 시를 이야기하지 마라\n내 시를 이야기하지 마라\n내 시를 이야기하지 마라\n내 시를 이야기하지 마라."

for c in d["chapters"]:
    if c["title"] == "@시쓰기":
        c["blocks"] = [{"type": "p", "text": poem1}]
    elif c["title"] == "@시":
        c["blocks"] = [{"type": "p", "text": poem2}]

with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("patched")
