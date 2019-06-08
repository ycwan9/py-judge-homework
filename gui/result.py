import tkinter as tk
from tkinter.simpledialog import Dialog
from tkinter.scrolledtext import ScrolledText

from tester import RESULTS


class ResultView(Dialog):
    """configure test cases"""

    def __init__(self, test_result):
        self.test_result = test_result
        super().__init__(tk._default_root, "评测结果")

    def body(self, master):
        master.pack(fill=tk.BOTH)
        self.resultlist = tk.Listbox(master)
        self.resultlist.pack(fill=tk.BOTH)
        self.resultlist.bind("<<ListboxSelect>>", self.cb_list)
        self.resultdetail = ScrolledText(master, state=tk.DISABLED)
        self.resultdetail.pack(fill=tk.BOTH)
        for case_name, ret, time_len, err_msg in self.test_result:
            item_color = "blue" if ret == "AC" else "red"
            self.resultlist.insert(
                tk.END, f"{ret} {time_len:0.3f}s {case_name}")
            self.resultlist.itemconfigure(tk.END, fg=item_color)

    def cb_list(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        pos = selection[0]
        case_name, ret, time_len, err_msg = self.test_result[pos]
        detail = f"""\
结果:\t{RESULTS[ret]}
时间:\t{time_len} s
测试点:\t{case_name}
{err_msg}"""
        self.resultdetail.config(state=tk.NORMAL)
        self.resultdetail.delete("1.0", tk.END)
        self.resultdetail.insert("1.0", detail)
        self.resultdetail.config(state=tk.DISABLED)
