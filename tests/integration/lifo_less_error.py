#!/usr/bin/env python3
import subprocess

for i in range(1, 120):
    with open("../../logs/error/logLi{}.out".format(i), "w") as f:
        subprocess.Popen(["../../dht_crawler/exec.py",
                          "--duration=900",
                          "--bind_port={}".format(i+22800),
                          "--magnet=../../examples/magnet-link_fedora"],
                          stdout=f)

