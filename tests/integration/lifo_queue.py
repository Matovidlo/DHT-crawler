#!/usr/bin/env python3
import subprocess

for i in range(10, 1800, 5):
    with open("../../logs/lifo_queue/logH{}.out".format(i), "w") as f:
        subprocess.Popen(["../../src/exec.py",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+40000),
                          "--hash=11516A493655C6ED33E0B12D6BA9C70C9F2E22AA"],
                          stdout=f)

