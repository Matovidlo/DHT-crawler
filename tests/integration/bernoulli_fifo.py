#!/usr/bin/env python3
import subprocess

with open("../../logs/test/logBF1.out", "w") as f:
    subprocess.Popen(["../../dht_crawler/exec.py",
                      "--duration=600",
                      "--fifo",
                      "--bind_port=4672",
                      "--magnet=../../examples/avengers_magnet"],
                     stdout=f)
