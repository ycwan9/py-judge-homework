from collections import UserList, namedtuple
from os.path import isfile


TestCase = namedtuple("TestCase", ("fin", "fout"))


class TestCaseList(UserList):
    """测试参数存储
    在列表中存储作为测试点（TestCase 对象）

    Attributes:
        time_limit: float 类型，秒为单位的运行时间限制
        mem_size: int，byte 为单位的运行内存限制，零值为不限制
        ignore_space: bool，开关忽略行末空白
        ignore_return: 同上，结尾空行
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.time_limit = 1.
        self.mem_size = 0
        self.ignore_space = True
        self.ignore_return = True

    def copy(self):
        ins = super().copy()
        ins.time_limit = self.time_limit
        ins.mem_size = self.mem_size
        ins.ignore_space = self.ignore_space
        ins.ignore_return = self.ignore_return
        return ins

    def set_fin(self, p, v):
        """设置 self[p].fin 为 v"""
        self.data[p] = self.data[p]._replace(fin=v)

    def set_fout(self, p, v):
        """设置 self[p].fout 为 v"""
        self.data[p] = self.data[p]._replace(fout=v)

    def add_case(self, finput, answer):
        """添加单个测试点 TestCase(finput, answer)"""
        self.data.append(TestCase(finput, answer))

    def discover_and_add(self, file_list):
        """根据测试文件列表自动扫描匹配并生成测试点

        Args:
            file_list: 包含输入文件的可迭代对象
        """
        in_files = []
        out_files = set()
        etc_files = []
        for fname in file_list:
            if fname.endswith(".in"):
                # input file
                in_files.append(fname)
            elif fname.endswith(".out"):
                # output
                out_files.add(fname)
            else:
                etc_files.append(fname)
        for fname in in_files:
            outname = fname[:-2] + "out"
            if outname in out_files:
                out_files.discard(outname)
                self.add_case(fname, outname)
                continue
            if isfile(outname):
                self.add_case(fname, outname)
            else:
                self.add_case(fname, "")
        for fname in out_files:
            inname = fname[:-3] + "in"
            if isfile(inname):
                self.add_case(inname, fname)
            else:
                self.add_case("", fname)
        for fname in etc_files:
            self.add_case(fname, "")
