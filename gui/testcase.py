import tkinter as tk
from tkinter.simpledialog import Dialog
import tkinter.filedialog as tkfd


class TestcaseView(Dialog):
    """configure test cases"""

    def __init__(self, testcases):
        self.testcases = testcases
        self.is_ok = False
        super().__init__(tk._default_root, "测试点")

    def apply(self):
        self.testcases.ignore_space = bool(self.space_v.get())
        self.testcases.ignore_return = bool(self.return_v.get())
        try:
            self.testcases.mem_size = int(self.mem_t.get())
        except ValueError:
            pass
        try:
            self.testcases.time_limit = float(self.time_t.get())
        except ValueError:
            pass
        self.is_ok = True

    def body(self, master):
        master.pack(fill=tk.BOTH)
        self.table_frame = tk.Frame(master)
        self.table_frame.rowconfigure(1, weight=1)
        for n, w in enumerate([10, 10, 1]):
            self.table_frame.columnconfigure(n, weight=w)
        self.table_frame.pack(fill=tk.BOTH)
        self.inputlist = tk.Listbox(self.table_frame, borderwidth=0)
        self.inputlist.grid(row=0, column=0, sticky=tk.N+tk.W+tk.S+tk.E)
        self.anslist = tk.Listbox(self.table_frame, borderwidth=0)
        self.anslist.grid(row=0, column=1, sticky=tk.N+tk.W+tk.S+tk.E)
        self.delbtnlist = tk.Listbox(self.table_frame, width=2, borderwidth=0)
        self.delbtnlist.grid(row=0, column=2, sticky=tk.N+tk.W+tk.S+tk.E)
        self.inputlist.insert(0, "[add...]")
        self.anslist.insert(0, "[add...]")
        self.delbtnlist.insert(0, "  ")
        _disable_scroll = lambda x: "break"
        for listbox in (self.inputlist, self.anslist, self.delbtnlist):
            listbox.bind("<<ListboxSelect>>", self.cb_list)
            listbox.bind("<MouseWheel>", _disable_scroll)
            listbox.bind("<Button-4>", _disable_scroll)
            listbox.bind("<Button-5>", _disable_scroll)
        self.draw_conf(master)
        self.update()

    def draw_conf(self, master):
        self.conf_box = tk.Frame(master)
        self.mem_l = tk.Label(self.conf_box, text="内存限制 (byte)")
        self.mem_l.grid(row=0, column=0)
        self.time_l = tk.Label(self.conf_box, text="时间限制 (s)")
        self.time_l.grid(row=1, column=0)
        self.mem_t = tk.Entry(self.conf_box)
        self.mem_t.insert(0, str(self.testcases.mem_size))
        self.mem_t.grid(row=0, column=1)
        self.time_t = tk.Entry(self.conf_box)
        self.time_t.insert(0, str(self.testcases.time_limit))
        self.time_t.grid(row=1, column=1)
        self.space_v = tk.IntVar()
        self.space_v.set(int(self.testcases.ignore_space))
        self.space_t = tk.Checkbutton(self.conf_box, text="忽略行末空格",
                                      variable=self.space_v)
        self.space_t.grid(row=2, column=0)
        self.return_v = tk.IntVar()
        self.return_v.set(int(self.testcases.ignore_return))
        self.return_t = tk.Checkbutton(self.conf_box, text="忽略空行",
                                       variable=self.return_v)
        self.return_t.grid(row=2, column=1)
        self.conf_box.pack(fill=tk.BOTH)

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

