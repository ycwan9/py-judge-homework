import os
import time
from sys import exc_info


def main(fdr, fdw, timelimit, memsize):
    code_len = int.from_bytes(os.read(fdr, 4), byteorder="big")
    code_str = os.read(fdr, code_len).decode("utf-8")
    proc = compile(code_str, "code", "exec")
    del code_str, code_len
    if memsize:
        try:
            import resource
            resource.prlimit(0, resource.RLIMIT_DATA,
                             (memsize, resource.RLIM_INFINITY))
        except ImportError:
            print("unsupportted platform")
    os.write(fdw, b"\0")
    try:
        start_time = time.perf_counter()
        exec(proc)
        end_time = time.perf_counter()
    except Exception:
        errinfo = exc_info()
        os.write(fdw, b"\1")
        import traceback
        err = traceback.format_exception(*errinfo).encode("utf-8")
        os.write(fdw, len(err).to_bytes(4, byteorder="big"))
        os.write(fdw, err)
    else:
        os.write(fdw, b"\0")
        os.write(fdw, int((end_time - start_time) * 1e3).to_bytes(
            4, byteorder="big"))


if __name__ == "__main__":
    from sys import argv
    _, fdr, fdw, timelimit, memsize = argv
    timelimit = float(timelimit)
    memsize = int(memsize)
    fdr = int(fdr)
    fdw = int(fdw)
    main(fdr, fdw, timelimit, memsize)

