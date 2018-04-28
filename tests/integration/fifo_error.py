#!/usr/bin/env python3
import subprocess

for i in range(1, 120):
    with open("../../logs/error/logF{}.out".format(i), "w") as f:
        subprocess.Popen(["../../dht_crawler/exec.py",
                          "--duration=900",
                          "--fifo",
                          "--bind_port={}".format(i+11800),
                          "--hash=11516A493655C6ED33E0B12D6BA9C70C9F2E22AA"],
                          stdout=f)

