#!/usr/bin/env python3
import subprocess

with open("../../logs/test/logBL1.out", "w") as f:
    subprocess.Popen(["../../dht_crawler/exec.py",
                      "--duration=600",
                      "--bind_port=4150",
                      "--magnet=../../examples/avengers_magnet"],
                     stdout=f)
