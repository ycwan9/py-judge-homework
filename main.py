#!/usr/bin/env python3
import tkinter as tk
from sys import argv

from gui.main import MainView
from testcase import TestCaseList

if __name__ == "__main__":
    if "-d" in argv:
        import logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    root = tk.Tk()
    testcases = TestCaseList()
    testcases.add_case("a", "b")
    app = MainView(root, testcases)
    app.mainloop()
