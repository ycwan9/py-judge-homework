import tkinter as tk
from tkinter.simpledialog import Dialog
import tkinter.filedialog as tkfd


class TestcaseView(Dialog):
    """configure test cases"""

    def __init__(self, testcases):
        self.testcases = testcases
        self.is_ok = False
        super().__init__(tk._default_root, "Select Testcases")

    def apply(self):
        self.is_ok = True

    def body(self, master):
        self.table_frame = tk.Frame(master)
        top = self.table_frame.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        for n, w in enumerate([10, 10, 1]):
            self.table_frame.columnconfigure(n, weight=w)
        self.table_frame.grid()
        self.inputlist = tk.Listbox(self.table_frame)
        self.inputlist.grid(row=0, column=0, sticky=tk.E)
        self.anslist = tk.Listbox(self.table_frame)
        self.anslist.grid(row=0, column=1, sticky=tk.E)
        self.delbtnlist = tk.Listbox(self.table_frame, width=2)
        self.delbtnlist.grid(row=0, column=2)
        self.inputlist.insert(0, "add...")
        self.anslist.insert(0, "add...")
        self.delbtnlist.insert(0, "  ")
        self.inputlist.bind("<<ListboxSelect>>", self.cb_list)
        self.anslist.bind("<<ListboxSelect>>", self.cb_list)
        self.delbtnlist.bind("<<ListboxSelect>>", self.cb_list)
        self.update()

    def update(self):
        self.inputlist.delete(1, tk.END)
        self.anslist.delete(1, tk.END)
        self.delbtnlist.delete(1, tk.END)
        for in_name, ans_name in self.testcases:
            self.inputlist.insert(tk.END, in_name)
            self.anslist.insert(tk.END, ans_name)
            self.delbtnlist.insert(tk.END, "\u2715")

    def cb_list(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        pos = selection[0]
        if pos == 0:
            # "add" is clicked
            names = tkfd.askopenfilenames()
            self.testcases.discover_and_add(names)
        else:
            pos -= 1
            if event.widget is self.delbtnlist:
                # delete the entry
                del self.testcases[pos]
            else:
                name = tkfd.askopenfilename()
                if name:
                    if event.widget is self.inputlist:
                        self.testcases.set_fin(pos, name)
                    elif event.widget is self.anslist:
                        self.testcases.set_fout(pos, name)
                    else:
                        assert False
        self.update()

