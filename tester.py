#!/usr/bin/env python3
import multiprocessing as mp
from tempfile import NamedTemporaryFile
import logging
import os
import signal
import time
from itertools import zip_longest
from sys import executable
import py_compile
import traceback

import testcase


RESULTS = {
    "AC": "Accepted",
    "WA": "Wrong Answer",
    "RE": "Runtime Error",
    "CE": "Compile Error",
    "TLE": "Time Limit Exceeded",
    "MLE": "Memory Limit Exceeded",
    "": ""}
_logger = logging.getLogger("tester")


def proc(args, time_limit, mem_size, start_time,
         _stdin_name, _stdout_name, _stderr_name):
    if mem_size:
        import resource
        resource.setrlimit(resource.RLIMIT_DATA, (mem_size, mem_size))
    _stdin_no = os.open(_stdin_name, os.O_RDONLY)
    _stdout_no = os.open(_stdout_name, os.O_WRONLY)
    _stderr_no = os.open(_stderr_name, os.O_WRONLY)
    os.dup2(_stdin_no, 0)
    os.dup2(_stdout_no, 1)
    os.dup2(_stderr_no, 2)
    start_time.value = time.perf_counter()
    os.execvp(args[0], args)


def watchdog(time_limit, pid):
    """kill pid after time_limit"""
    time.sleep(time_limit)
    os.kill(pid, signal.SIGKILL)


def test(args, time_limit, mem_size, ignore_space, ignore_return,
         input_name, answer_name):
    time_limit = float(time_limit)
    mem_size = int(mem_size)
    return run_test(args, time_limit, mem_size, input_name,
                    lambda f: check(f, answer_name,
                                    ignore_space, ignore_return))


def test_list(code_str, testcases: testcase.TestCaseList):
    with NamedTemporaryFile("w", prefix="runner_", suffix=".py") as fsource:
        fsource.write(code_str)
        fsource.flush()
        try:
            py_compile.compile(fsource.name)
        except:
            err_msg = traceback.format_exc()
            _logger.debug("compile error: %s", err_msg)
            yield "CE", 0., err_msg
        else:
            for input_name, answer_name in testcases:
                yield test([executable, fsource.name],
                           testcases.time_limit, testcases.mem_size,
                           testcases.ignore_space, testcases.ignore_return,
                           input_name, answer_name)


def run_test(args, time_limit, mem_size, stdin_name, out_checker):
    logger = _logger.getChild(f"test_{args[0]}")
    start_time = mp.Value("d")
    start_time.value = 0
    with NamedTemporaryFile(prefix="runner_stdout") as fout,\
            NamedTemporaryFile(prefix="runner_stderr") as ferr:
        logger.debug("redirecting stdout to %s", fout.name)
        logger.debug("redirecting stderr to %s", ferr.name)
        test_proc = mp.Process(target=proc,
                               args=(args, time_limit, mem_size, start_time,
                                     stdin_name, fout.name, ferr.name))
        test_proc.start()
        watch_proc = mp.Process(target=watchdog,
                                args=(time_limit + 1., test_proc.pid))
        watch_proc.start()
        _, exit_status = os.waitpid(test_proc.pid, 0)
        end_time = time.perf_counter()
        watch_proc.terminate()
        logger.debug("process %s end with %s", args, exit_status)
        time_elapsed = end_time - start_time.value
        logger.debug("start: %f, end: %f, time: %f",
                     start_time.value, end_time, time_elapsed)
        if time_elapsed > time_limit:
            logger.debug("result: TLE")
            return "TLE", time_elapsed, ""
        err_msg = ""
        if exit_status == 0:
            result = "AC" if out_checker(fout) else "WA"
        else:
            err_msg = ferr.read()
            logger.debug("stderr: %s", err_msg)
            result = parse_err(err_msg)
        logger.debug("result: %s", result)
        return result, time_elapsed, err_msg


def check(fout, ans, ignore_space, ignore_return):
    ignore_chars = b"\r\n"
    if ignore_space:
        ignore_chars += b"\t "
    blank_val = b"" if ignore_return else b"\n__invalid__"
    with open(ans, "rb") as fans:
        for line_out, line_ans in zip_longest(fout, fans, fillvalue=blank_val):
            if line_out.rstrip(ignore_chars) != line_ans.strip(ignore_chars):
                return False
    return True


def parse_err(err_msg):
    try:
        *_, err_line = filter(bool, err_msg.split(b"\n"))
        err_type = err_line.split(b":")[0]
        ret = {
            b"MemoryError": "MLE",
            b"SyntaxError": "CE",
            b"NameError": "CE"
        }.get(err_type)
        if ret:
            return ret
    except IndexError:
        pass
    return "RE"


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    from sys import argv
    _, time_limit, mem_size, stdin_name, ans_name, *args = argv
    time_limit = float(time_limit)
    mem_size = int(mem_size)
    print(test(args, time_limit, mem_size, stdin_name, ans_name, "strip"))
