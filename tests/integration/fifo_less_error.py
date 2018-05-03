#!/usr/bin/env python3
import subprocess

for i in range(1, 200):
    with open("../../logs/error/logFi{}.out".format(i), "w") as f:
        subprocess.Popen(["../../dht_crawler/exec.py",
                          "--duration=900",
                          "--fifo",
                          "--bind_port={}".format(i+12800),
                          "--magnet=../../examples/magnet-link_fedora"],
                          stdout=f)

