import unittest
import unittest.mock as mock
import os.path

import testcase

MOCKED_INPUTS = tuple(f"data{i}.in" for i in range(10))
MOCKED_OUTPUTS = tuple(f"data{i}.out" for i in range(5, 15))
MOCKED_FILES = MOCKED_INPUTS + MOCKED_OUTPUTS


class TestTestcase(unittest.TestCase):
    def test_append(self):
        flist = list(zip(map(str, range(10)), map(str, range(10, 20))))
        cases = [testcase.TestCase(a, b) for a, b in flist]
        caselist = testcase.TestCaseList()
        for a, b in flist:
            caselist.add_case(a, b)
        self.assertEqual(caselist, testcase.TestCaseList(cases))

    @mock.patch("testcase.isfile", side_effect=lambda x: x in MOCKED_FILES)
    def test_discover_fout(self, mod_path):
        caselist = testcase.TestCaseList()
        caselist.discover_and_add(["data3.in", "data5.in", "data8.in"])
        caseout = testcase.TestCaseList()
        for a, b in [("data3.in", ""),
                     ("data5.in", "data5.out"),
                     ("data8.in", "data8.out")]:
            caseout.add_case(a, b)
        self.assertEqual(set(caselist), set(caseout))

    @mock.patch("testcase.isfile", side_effect=lambda x: x in MOCKED_FILES)
    def test_discover_fin(self, mod_path):
        caselist = testcase.TestCaseList()
        caselist.discover_and_add(["data12.out", "data5.out", "data8.out"])
        caseout = testcase.TestCaseList()
        for a, b in [("", "data12.out"),
                     ("data5.in", "data5.out"),
                     ("data8.in", "data8.out")]:
            caseout.add_case(a, b)
        self.assertEqual(set(caselist), set(caseout))

    @mock.patch("testcase.isfile", side_effect=lambda x: x in MOCKED_FILES)
    def test_discover_both(self, mod_path):
        caselist = testcase.TestCaseList()
        caselist.discover_and_add(["data5.out", "data8.out",
                                   "data5.in", "data8.in"])
        caseout = testcase.TestCaseList()
        for a, b in [("data5.in", "data5.out"),
                     ("data8.in", "data8.out")]:
            caseout.add_case(a, b)
        self.assertEqual(set(caselist), set(caseout))

    @mock.patch("testcase.isfile", side_effect=lambda x: x in MOCKED_FILES)
    def test_discover_unkonwn(self, mod_path):
        caselist = testcase.TestCaseList()
        caselist.discover_and_add([i for i in "abcd"])
        caseout = testcase.TestCaseList()
        for a in "abcd":
            caseout.add_case(a, "")
        self.assertEqual(set(caselist), set(caseout))
