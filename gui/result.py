import tkinter as tk
from tkinter.simpledialog import Dialog
from tkinter.scrolledtext import ScrolledText


class ResultView(Dialog):
    """configure test cases"""

    def __init__(self, test_result):
        self.test_result = test_result
        super().__init__(tk._default_root, "Test Result")

    def body(self, master):
        self.resultlist = tk.Listbox(master)
        self.resultlist.grid(row=0, column=0, sticky=tk.W+tk.E)
        self.resultlist.bind("<<ListboxSelect>>", self.cb_list)
        self.resultdetail = ScrolledText(master)
        self.resultdetail.grid(row=1, column=0)
        for case_name, ret, time_len, err_msg in self.test_result:
            self.resultlist.insert(tk.END, f"{case_name} {ret} {time_len}")

    def cb_list(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        pos = selection[0]
        *_, err_msg = self.test_result[pos]
        self.resultdetail.delete("1.0", tk.END)
        self.resultdetail.insert("1.0", err_msg)


