#!/usr/bin/env python3
import subprocess

for i in range(10, 900, 5):
    with open("../../logs/nodes_timer/logF{}.out".format(i), "w") as f:
        subprocess.Popen(["../../src/exec.py",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+29000),
                          "--file=../../examples/Chasin_Coral2017_1080p.torrent",],
                          stdout=f)
