import os
import time


def main(path, args, fdr, fdw, timelimit, memsize):
    if memsize:
        try:
            import resource
            resource.prlimit(0, resource.RLIMIT_DATA,
                             (memsize, resource.RLIM_INFINITY))
        except ImportError:
            print("unsupportted platform")
    code_len = int.from_bytes(os.read(fdr, 4), byteorder="big")
    code_str = os.read(fdr, code_len).decode("utf-8")
    proc = compile(code_str, "code")
    del code_str, code_len
    os.write(fdw, b"\0")
    exec(proc)
    os.execvp(path, args)


if __name__ == "__main__":
    from sys import argv
    _, fdr, fdw, timelimit, memsize, *exe_args = argv
    timelimit = float(timelimit)
    memsize = int(memsize)
    fdr = int(fdr)
    fdw = int(fdw)
    main(exe_args[0], exe_args, fdr, fdw, timelimit, memsize)

