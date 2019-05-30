#!/usr/bin/env python3
import tkinter as tk

from gui.main import MainView
from testcase import TestCaseList

if __name__ == "__main__":
    root = tk.Tk()
    testcases = TestCaseList()
    testcases.add_case("a", "b")
    app = MainView(root, testcases)
    app.mainloop()
