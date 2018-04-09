#!/usr/bin/env python3
import subprocess

for i in range(50, 3600, 4):
    with open("../logs/nodes_timer/logF{}.out".format(i), "w") as f:
        subprocess.Popen(["../src/exec.py",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+4000),
                          "--file=../examples/Chasin_Coral2017_1080p.torrent",],
                          stdout=f)
