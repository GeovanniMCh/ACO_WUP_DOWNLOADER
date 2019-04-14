try:
    import ttk
    from Tkinter import Text
except ImportError:
    from tkinter import ttk, Text



class ProgressTab(ttk.Frame):
    def __init__(self, master=None, gui=None):
        ttk.Frame.__init__(self, master=master)
        lang = gui.get_gui_language()
        
        t5_frm1 = ttk.Frame(self)
        t5_frm2 = ttk.Frame(self)
        t5_frm3 = ttk.Frame(self)
        t5_frm4 = ttk.Frame(self)
        t5_frm5 = ttk.Frame(self)
        t5_frm6 = ttk.Frame(self)
        t5_frm7 = ttk.Frame(self)
        t5_frm8 = ttk.Frame(self)
        t5_frm9 = ttk.Frame(self)
        t5_frm10 = ttk.Frame(self)
        t5_frm11 = ttk.Frame(self)

        ttk.Label(t5_frm1, text=lang['Total download progress:'], font='Helvetica 10 bold').pack(side='left')
        gui.progressbar = ttk.Progressbar(t5_frm1, orient='horizontal', length=325, mode='determinate')
        gui.progressbar.pack(padx=10, side='left')
        ttk.Label(t5_frm1, textvariable=gui.dl_percentage_string).pack(side='left', padx=10)
        ttk.Label(t5_frm1, textvariable=gui.dl_progress_string).pack(side='left')
        ttk.Label(t5_frm1, text='/').pack(side='left')
        ttk.Label(t5_frm1, textvariable=gui.dl_total_string).pack(side='left')
        ttk.Button(t5_frm1, text=lang['stop download'], command=gui.abort_download_session).pack(side='left', padx=10)
        ttk.Button(t5_frm1, text=lang['resume download'], command=gui.resume_download_session).pack(side='left', padx=10)
        ttk.Label(t5_frm3, text=lang['Status:'], font='Helvetica 10 bold').pack(side='left')
        ttk.Label(t5_frm4, textvariable=gui.thread1_status).pack(padx=10, side='left')
        ttk.Label(t5_frm5, textvariable=gui.thread2_status).pack(padx=10, side='left')
        ttk.Label(t5_frm6, textvariable=gui.thread3_status).pack(padx=10, side='left')
        ttk.Label(t5_frm7, textvariable=gui.thread4_status).pack(padx=10, side='left')
        ttk.Label(t5_frm8, textvariable=gui.thread5_status).pack(padx=10, side='left')
        ttk.Label(t5_frm9, text=lang['FAILED downloads:'], font='Helvetica 10 bold').pack(side='bottom')
        failed_scroller = ttk.Scrollbar(t5_frm10, orient='vertical')
        failed_scroller.pack(side='right', fill='y')
        gui.failed_box = Text(t5_frm10, width=20, height=8, state='disabled')
        gui.failed_box.pack(side='right', fill='both', expand=True)
        gui.failed_box.config(yscrollcommand=failed_scroller.set)
        failed_scroller.config(command=gui.failed_box.yview)
        log_scroller = ttk.Scrollbar(t5_frm11, orient='vertical')
        log_scroller.pack(side='right', fill='y')
        gui.log_box = Text(t5_frm11, state='normal')
        gui.log_box.pack(side='right', fill='both', expand=True)
        gui.log_box.config(yscrollcommand=log_scroller.set)
        log_scroller.config(command=gui.log_box.yview)
        ttk.Label(t5_frm11, text=lang['Log:'], font='Helvetica 10 bold').pack(side='top', padx=15)

        t5_frm1.grid(row=0, column=1, columnspan=5, padx=10, pady=10, sticky='w')
        t5_frm2.grid(row=0, column=6, columnspan=4, padx=10, pady=10, sticky='w')
        t5_frm3.grid(row=1, column=1, padx=10, pady=0, sticky='w')
        t5_frm4.grid(row=2, column=1, columnspan=6, padx=10, pady=0, sticky='w')
        t5_frm5.grid(row=3, column=1, columnspan=6, padx=10, pady=0, sticky='w')
        t5_frm6.grid(row=4, column=1, columnspan=6, padx=10, pady=0, sticky='w')
        t5_frm7.grid(row=5, column=1, columnspan=6, padx=10, pady=0, sticky='w')
        t5_frm8.grid(row=6, column=1, columnspan=6, padx=10, pady=0, sticky='w')
        t5_frm9.grid(row=21, column=1, padx=10, sticky='sw')
        t5_frm10.grid(row=22, column=1, columnspan=2, rowspan=6, padx=10, pady=5, sticky='nsew')
        t5_frm11.grid(row=7, column=5, columnspan=8, rowspan=20, pady=5, sticky='nsew')

