import unittest
import logging
import os

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

    def test_strip(self):
        for fname, out_prefix in get_progs(r"(strip_\w+).in", 2):
            with self.subTest(name=fname):
                ret, *_ = tester.test(["cat"], 1., 0, True, True,
                                      f"test_codes/{fname}",
                                      f"test_codes/{out_prefix}.out")
                self.assertEqual(ret, "AC")

    def test_strip_neg(self):
        for fname, out_prefix in get_progs(r"(strip_\w+).in", 2):
            with self.subTest(name=fname):
                ret, *_ = tester.test(["cat"], 1., 0, False, False,
                                      f"test_codes/{fname}",
                                      f"test_codes/{out_prefix}.out")
                self.assertEqual(ret, "WA")

    def test_strict(self):
        for _, fname, expected_ret in get_progs(r"(prog\w*_([A-Z]+)).py", 3):
            with self.subTest(name=fname):
                prefix = f"test_codes/{fname}"
                ret, *_ = tester.test(["python3", prefix+".py"], 1.,
                                      16*1024**2, False, False, prefix+".in",
                                      prefix+".out")
                self.assertEqual(ret, expected_ret)

    def test_list(self):
        testcases = testcase.TestCaseList()
        for _ in range(5):
            testcases.add_case("test_codes/prog_AC.in",
                               "test_codes/prog_AC.out")
        with open("test_codes/prog_AC.py") as f:
            source_str = f.read()
            for ret, *_ in tester.test_list(source_str, testcases):
                self.assertEqual(ret, "AC")
