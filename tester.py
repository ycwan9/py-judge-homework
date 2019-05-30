#!/usr/bin/env python3
import subprocess
import os
import time


def run(code_str, timelimit, memsize):
    code_b = code_str.encode("utf-8")
    fdr, fdw_p = os.pipe()
    os.set_inheritable(fdw_p, True)
    fdr_p, fdw = os.pipe()
    os.set_inheritable(fdr_p, True)
    proc = subprocess.Popen(["python3", "exec.py", str(fdr_p), str(fdw_p),
                             str(timelimit), str(memsize)],
                            shell=False,
                            close_fds=False)
    os.write(fdw, len(code_b).to_bytes(4, byteorder="big"))
    os.write(fdw, code_b)
    print(repr(os.read(fdr, 1)))
    start_time = time.perf_counter()
    end_time = .0
    try:
        proc.wait(timelimit + 1)
        end_time = time.perf_counter()
    except subprocess.TimeoutExpired:
        print("tle")
        proc.kill()
        return
    ret = os.read(self.


if __name__ == "__main__":
    from sys import argv
    _, timelimit, memsize, fname = argv
    timelimit = float(timelimit)
    memsize = int(memsize)
    with open(fname) as f:
        run(f.read(), timelimit, memsize)

