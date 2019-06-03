import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import Dialog

from .testcase import TestcaseView
from .result import ResultView
from tester import test_list


class MainView(tk.Frame):
    """root window"""

    def __init__(self, master, testcases):
        super().__init__(master)
        self.master = master
        self.testcases = testcases
        self.grid(sticky=tk.N+tk.W+tk.S+tk.E)
        top = self.winfo_toplevel()
        top.grid()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        for i in range(3):
            self.columnconfigure(i, weight=1)
        for i in range(2):
            self.columnconfigure(i)
        self.__create_widgets()

    def __create_widgets(self):
        sticky_opts = tk.N+tk.W+tk.S+tk.E
        self.source_input = ScrolledText(self)
        self.testcase_button = tk.Button(self, text="testcase",
                                         command=self.cb_testcase)
        self.submit_button = tk.Button(self, text="submit",
                                       command=self.cb_submit)
        self.clear_button = tk.Button(self, text="clear",
            command=lambda : self.source_input.delete("1.0", tk.END))
        self.source_input.grid(columnspan=3, stick=sticky_opts)
        self.testcase_button.grid(row=1, column=0)
        self.submit_button.grid(row=1, column=1)
        self.clear_button.grid(row=1, column=2)

    def cb_testcase(self):
        testcases = self.testcases.copy()
        window = TestcaseView(testcases)
        if window.is_ok:
            self.testcases = window.testcases
            print(self.testcases)

    def cb_submit(self):
        source = self.source_input.get("1.0", tk.END)
        result = [(testcase[0],) + ret for testcase, ret in
                  zip(self.testcases, test_list(source, self.testcases))]
        ResultView(result)
