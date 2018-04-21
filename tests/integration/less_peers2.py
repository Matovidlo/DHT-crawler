#!/usr/bin/env python3
import subprocess

for i in range(50, 3600, 4):
    with open("../logs/less_peers/logFed{}.out".format(i), "w") as f:
        subprocess.Popen(["../src/exec.py",
                          "--duration={}".format(i),
                          "--bind_port={}".format(i+13500),
                          "--magnet=../examples/magnet-link_fedora"],
                          stdout=f)

