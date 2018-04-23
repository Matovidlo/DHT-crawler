#!/usr/bin/env python3
import subprocess

for i in range(10, 90, 5):
    with open("../../logs/test/logH{}.out".format(i), "w") as f:
        subprocess.Popen(["../../src/exec.py",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+11800),
                          "--hash=11516A493655C6ED33E0B12D6BA9C70C9F2E22AA"],
                          stdout=f)

