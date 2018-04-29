#!/usr/bin/env python3
import subprocess

for i in range(1, 120):
    with open("../../logs/error/logF{}.out".format(i), "w") as f:
        subprocess.Popen(["../../dht_crawler/exec.py",
                          "--duration=900",
                          "--fifo",
                          "--bind_port={}".format(i+11800),
                          "--magnet=../../examples/magnet-link_fedora"],
                          stdout=f)

