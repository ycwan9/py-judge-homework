import unittest
import logging
import os
from os.path import sep
from sys import executable

import tester
import testcase


def get_progs(exp, group_num):
    import re
    from os import scandir
    code_pattern = re.compile(exp)
    with scandir("test_codes") as i:
        for f in i:
            if f.is_file():
                fname = f.name
                ret = code_pattern.fullmatch(fname)
                if ret:
                    yield tuple(ret.group(i) for i in range(group_num))


class TesterTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig()
        if os.getenv("DEBUG_LOGGER", False):
            logging.getLogger().setLevel(logging.DEBUG)

    @unittest.skipIf(tester._mswindows, "skip MS Windows")
    def test_strip(self):
        for fname, out_prefix in get_progs(r"(strip_\w+).in", 2):
            with self.subTest(name=fname):
                ret, *_ = tester.test(["cat"], 1., 0, True, True,
                                      f"test_codes{sep}{fname}",
                                      f"test_codes{sep}{out_prefix}.out")
                self.assertEqual(ret, "AC")

    @unittest.skipIf(tester._mswindows, "skip MS Windows")
    def test_strip_neg(self):
        for fname, out_prefix in get_progs(r"(strip_\w+).in", 2):
            with self.subTest(name=fname):
                ret, *_ = tester.test(["cat"], 1., 0, False, False,
                                      f"test_codes{sep}{fname}",
                                      f"test_codes{sep}{out_prefix}.out")
                self.assertEqual(ret, "WA")

    def test_strict(self):
        for _, fname, expected_ret in get_progs(r"(prog\w*_([A-Z]+)).py", 3):
            with self.subTest(name=fname):
                prefix = f"test_codes{sep}{fname}"
                ret, *_ = tester.test([executable, prefix+".py"], 1.,
                                      16*1024**2, False, False, prefix+".in",
                                      prefix+".out")
                self.assertEqual(ret, expected_ret)

    def test_list(self):
        testcases = testcase.TestCaseList()
        for _ in range(5):
            testcases.add_case(f"test_codes{sep}prog_AC.in",
                               f"test_codes{sep}prog_AC.out")
        with open(f"test_codes{sep}prog_AC.py") as f:
            source_str = f.read()
            for ret, *_ in tester.test_list(source_str, testcases):
                self.assertEqual(ret, "AC")
