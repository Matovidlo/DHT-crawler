#!/usr/bin/env python3
import subprocess

for i in range(10, 900, 5):
    with open("../../logs/nodes_timer/logH{}.out".format(i), "w") as f:
        subprocess.Popen(["../../dht_crawler/exec.py",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+9800),
                          "--hash=11516A493655C6ED33E0B12D6BA9C70C9F2E22AA"],
                          stdout=f)

