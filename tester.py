#!/usr/bin/env python3
import multiprocessing as mp
from tempfile import TemporaryDirectory, NamedTemporaryFile
import logging
import os
import time
from itertools import zip_longest
from sys import executable
import py_compile
import traceback
import sys
import subprocess


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
_mswindows = (sys.platform == "win32")


def proc(args, time_limit, mem_size, time_elapsed, return_val, _stdin_name,
         _stdout_name, _stderr_name):
    """测试的 runner 函数

    Args:
        args: 待测程序及其参数的列表
        time_limit: float，秒为单位的运行时间限制
        mem_size: int，byte 为单位的运行内存限制，零值为不限制
        time_elapsed: double 类型的 multiprocessing 中的 shared_ctypes 对象
            用以存储并返回实际运行时间
        return_val: int 类型的 multiprocessing 中的 shared_ctypes 对象
            用以存储并返回待测程序的返回值
        _stdin_name, _stdout_name, _stderr_name: 为文件路径
            分别为待测程序的标准输入、输出、错误输出的重定向目标
    """
    if mem_size:
        try:
            if _mswindows:
                import win32api
                import win32job
                job = win32job.CreateJobObject(None, "judge_mem_limiter")
                win32job.SetInformationJobObject(
                    job,
                    win32job.JobObjectExtendedLimitInformation,
                    {
                        "BasicLimitInformation": {
                            "PerProcessUserTimeLimit": 0,
                            "PerJobUserTimeLimit": 0,
                            "LimitFlags":
                            win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY,
                            "MinimumWorkingSetSize": 0,
                            "MaximumWorkingSetSize": 0,
                            "ActiveProcessLimit": 0,
                            "Affinity": 0,
                            "PriorityClass": 0,
                            "SchedulingClass": 0
                        },
                        "IoInfo": {
                            "ReadOperationCount": 0,
                            "WriteOperationCount": 0,
                            "OtherOperationCount": 0,
                            "ReadTransferCount": 0,
                            "WriteTransferCount": 0,
                            "OtherTransferCount": 0,
                        },
                        "JobMemoryLimit": 0,
                        "PeakProcessMemoryUsed": 0,
                        "PeakJobMemoryUsed": 0,
                        "ProcessMemoryLimit": mem_size})
                win32job.AssignProcessToJobObject(
                    job, win32api.GetCurrentProcess())
            else:
                import resource
                resource.setrlimit(resource.RLIMIT_DATA, (mem_size, mem_size))
        except:
            _logger.error("unable to set memory limit under win32: %s",
                          traceback.format_exc())
    with open(_stdin_name, "rb") as stdin,\
            open(_stdout_name, "wb") as stdout,\
            open(_stderr_name, "wb") as stderr:
        proc = subprocess.Popen(args, stdin=stdin,
                                stdout=stdout, stderr=stderr)
        t_start = time.perf_counter()
        try:
            proc.wait(timeout=time_limit + 1.)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.returncode = -1
        t_end = time.perf_counter()
        time_elapsed.value = t_end - t_start
        return_val.value = proc.returncode


def test(args, time_limit, mem_size, ignore_space, ignore_return,
         input_name, answer_name):
    """对单个测试点运行测试
    封装了 run_test

    Args:
        args: 待测程序及其参数的列表
        time_limit: float，秒为单位的运行时间限制
        mem_size: int，byte 为单位的运行内存限制，零值为不限制
        ignore_space: bool，开关忽略行末空白
        ignore_return: 同上，结尾空行
        input_name: 输入文件
        answer_name: 标准答案

    Returns:
        三元组 (result, time_elapsed, err_msg)
        result: str，错误类型
        time_elapsed: float，用时
        err_msg: str，错误信息
    """
    time_limit = float(time_limit)
    mem_size = int(mem_size)
    return run_test(args, time_limit, mem_size, input_name,
                    lambda f: check(f, answer_name,
                                    ignore_space, ignore_return))


def test_list(code_str, testcases: testcase.TestCaseList):
    """对一个 TestCaseList 运行测试

    Args:
        code_str: 待测代码
        testcases: 将要运行的 TestCaseList 对象

    Returns:
	    一个迭代器，包含 test 函数对于每个测试点返回的三元组
    """
    with NamedTemporaryFile("w", prefix="runner_", suffix=".py",
                            delete=False) as fsource:
        fsource.write(code_str)
        script_name = fsource.name
    try:
        cfile = py_compile.compile(script_name)
    except:
        err_msg = traceback.format_exc()
        _logger.debug("compile error: %s", err_msg)
        yield "CE", 0., err_msg
    else:
        for input_name, answer_name in testcases:
            yield test([executable, script_name],
                       testcases.time_limit, testcases.mem_size,
                       testcases.ignore_space, testcases.ignore_return,
                       input_name, answer_name)
        os.remove(cfile)
    finally:
        os.remove(script_name)


def run_test(args, time_limit, mem_size, stdin_name, out_checker):
    """对单个测试点运行测试

    Args:
        args: 待测程序及其参数的列表
        time_limit: float，秒为单位的运行时间限制
        mem_size: int，byte 为单位的运行内存限制，零值为不限制
        stdin_name: 输入文件
        out_checker: 答案比较器

    Returns:
        三元组 (result, time_elapsed, err_msg)
        result: str，错误类型
        time_elapsed: float，用时
        err_msg: str，错误信息
    """
    logger = _logger.getChild(f"test_{args[0]}")
    result = ""
    time_elapsed = .0
    err_msg = ""
    mp_time = mp.Value("d")
    mp_return = mp.Value("i")
    with TemporaryDirectory() as dirname:
        logger.debug("redirecting to %s", dirname)
        stdout_name = os.path.join(dirname, "stdout")
        stderr_name = os.path.join(dirname, "stderr")
        logger.debug("redirecting stdout to %s", stdout_name)
        logger.debug("redirecting stderr to %s", stderr_name)
        for fn in stdout_name, stderr_name:
            open(fn, "a").close()
        test_proc = mp.Process(
            target=proc,
            args=(args, time_limit, mem_size, mp_time, mp_return,
                  stdin_name, stdout_name, stderr_name))
        test_proc.start()
        test_proc.join()
        exit_status = mp_return.value
        time_elapsed = mp_time.value
        logger.debug("process %s end with %s", args, exit_status)
        logger.debug("time: %f", time_elapsed)
        err_msg = ""
        with open(stdout_name, "rb") as fout, open(stderr_name, "rb") as ferr:
            err_msg = ferr.read()
            logger.debug("stderr: %s", err_msg)
            if time_elapsed > time_limit:
                result = "TLE"
            elif exit_status == 0:
                result = "AC" if out_checker(fout) else "WA"
            else:
                result = parse_err(err_msg)
            logger.debug("result: %s", result)
    return result, time_elapsed, err_msg.decode()


def check(fout, ans, ignore_space, ignore_return):
    """检查输出

    Args:
        fout: file object, 待测程序的输出
        ans: str，标准答案文件
        ignore_space: bool，开关忽略行末空白
        ignore_return: 同上，结尾空行
    """
    ignore_chars = b"\r\n"
    if ignore_space:
        ignore_chars += b"\t "
    blank_val = b"" if ignore_return else b"\n__invalid__"
    with open(ans, "rb") as fans:
        for line_out, line_ans in zip_longest(fout, fans, fillvalue=blank_val):
            _logger.debug("parsing line: %s", line_out)
            if line_out.rstrip(ignore_chars) != line_ans.strip(ignore_chars):
                return False
    return True


def parse_err(err_msg):
    """从 stderr 输出中提取 Exception Name 并判断错误类型"""
    try:
        *_, err_line = filter(bool, err_msg.split(b"\n"))
        err_type = err_line.strip(b"\r").split(b":")[0]
        ret = {
            b"MemoryError": "MLE",
            b"SyntaxError": "CE",
            b"NameError": "CE"
        }.get(err_type)
        if ret:
            return ret
    except (IndexError, ValueError):
        pass
    return "RE"


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    from sys import argv
    _, time_limit, mem_size, stdin_name, ans_name, *args = argv
    time_limit = float(time_limit)
    mem_size = int(mem_size)
    print(test(args, time_limit, mem_size, True, True, stdin_name, ans_name))
