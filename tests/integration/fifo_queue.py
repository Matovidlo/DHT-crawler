#!/usr/bin/env python3
import subprocess

for i in range(50, 3600, 4):
    with open("../logs/fifo_queue/logH{}.out".format(i), "w") as f:
        subprocess.Popen(["../src/exec.py",
                          "--fifo",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+45000),
                          "--hash=11516A493655C6ED33E0B12D6BA9C70C9F2E22AA"],
                          stdout=f)

