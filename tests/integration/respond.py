#!/usr/bin/env python3
import subprocess

for i in range(1, 100):
    with open("../../logs/respond/log{}.out".format(i), "w") as f:
        subprocess.Popen(["../../dht_crawler/exec.py",
                          "--duration={}".format(i * 5),
                          "--bind_port={}".format(i + 23500),
                          "--magnet=../../examples/avengers_magnet"],
                         stdout=f)
