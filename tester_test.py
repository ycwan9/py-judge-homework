import unittest


def get_progs():
    import re
    from os import scandir
    code_pattern = re.compile(r"(prog\w+_([A-Z]+)).py")
    with scandir("test_codes") as i:
        for f in i:
            if f.is_file():
                fname = f.name
                ret = code_pattern.fullmatch(fname)
                if ret:
                    yield fname, ret.group(1)


def build_test(code, testcases, **kwargs): pass


class TesterTest(unittest.TestCase):
    def test_progs(self):
        for fname, expected_ret, opts in get_progs():
            with self.subTest(name=fname):
                tester = build_test(fname+".py",
                                    (fname+".in", fname+".out"))
                ret = tester.run()
                self.assertEqual(ret.result, expected_ret)
