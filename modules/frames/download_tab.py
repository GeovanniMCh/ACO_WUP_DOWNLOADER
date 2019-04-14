try:
    import ttk
    from Tkinter import Listbox
except ImportError:
    from tkinter import ttk
    from tkinter import Listbox



class DownloadTab(ttk.Frame):
    def __init__(self, master=None, gui=None):
        ttk.Frame.__init__(self, master=master)
        lang = gui.get_gui_language()
        
        t2_frm0 = ttk.Frame(self)
        t2_frm1 = ttk.Frame(self)
        t2_frm2 = ttk.Frame(self)
        t2_frm3 = ttk.Frame(self)
        t2_frm4 = ttk.Frame(self)
        t2_frm5 = ttk.Frame(self)
        t2_frm6 = ttk.Frame(self)
        t2_frm7 = ttk.Frame(self)
        t2_frm8 = ttk.Frame(self)
        t2_frm9 = ttk.Frame(self)
        t2_frm10 = ttk.Frame(self)
        t2_frm11 = ttk.Frame(self)
        t2_frm12 = ttk.Frame(self)
        t2_frm13 = ttk.Frame(self)
        t2_frm14 = ttk.Frame(self)
        t2_frm15 = ttk.Frame(self)

        lbl = ttk.Label(t2_frm0,
                        text=lang[('Enter as many Title ID\'s as you would like to the list. Use the search box to filter titles '
                                   'that contain your search term. You can also enter a title id manually.')]).pack(padx=5, pady=16)

        ttk.Label(t2_frm1, text=lang['Choose regions to display:'], font='Helvetica 10 bold').pack(padx=15, pady=5,
                                                                                                   side='left')
        
        ttk.Checkbutton(t2_frm1, text='USA', variable=gui.filter_usa, 
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm1, text='EUR', variable=gui.filter_eur,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm1, text='JPN', variable=gui.filter_jpn,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Label(t2_frm2, text=lang['Choose content to display:'], font='Helvetica 10 bold').pack(padx=15, pady=5,
                                                                                             side='left')
        ttk.Checkbutton(t2_frm2, text=lang['Game'], variable=gui.filter_game,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm2, text=lang['Update'], variable=gui.filter_update,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm2, text='DLC', variable=gui.filter_dlc,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm2, text=lang['Demo'], variable=gui.filter_demo,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm2, text=lang['System'], variable=gui.filter_system,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Checkbutton(t2_frm2, text=lang['Only show items with a legit ticket'], variable=gui.filter_hasticket,
                        command=lambda: gui.populate_selection_list(download_data=False)).pack(padx=5, pady=5,
                                                                                                side='left')
        ttk.Label(t2_frm3, text=lang['Selection:'], font='Helvetica 10 bold').pack(padx=15, pady=7, side='top', anchor='w')

        sel_scroller = ttk.Scrollbar(t2_frm3, orient='vertical')
        gui.selection_box = Listbox(t2_frm3)
        gui.selection_box.pack(side='left', fill='both', expand=True)
        sel_scroller.pack(side='left', fill='y')
        gui.selection_box.config(yscrollcommand=sel_scroller.set)
        sel_scroller.config(command=gui.selection_box.yview)
        gui.selection_box.bind('<<ListboxSelect>>', gui.selection_box_changed)
        gui.selection_box.bind('<<Up>>', gui.selection_box_changed)
        ttk.Label(t2_frm9, text=lang['Search:'], font='Helvetica 10 bold').pack(padx=15, pady=7, side='left')
        ttk.Entry(t2_frm9, width=30, textvariable=gui.user_search_var, style="EntryStyle.TEntry").pack(side='left')
        ttk.Label(t2_frm4, text=lang['Title ID:'], font='Helvetica 10 bold').pack(padx=15, pady=7, side='left')
        gui.id_box = ttk.Entry(t2_frm4, width=20, textvariable=gui.idvar, style="EntryStyle.TEntry")
        gui.id_box.pack(padx=5, pady=5, side='left')
        ttk.Label(t2_frm5, text=lang['Key:'], font='Helvetica 10 bold').pack(padx=15, pady=7, side='left', anchor='n')
        gui.key_box = ttk.Entry(t2_frm5, width=34, style="EntryStyle.TEntry")
        gui.key_box.pack(padx=5, pady=5, side='left')
        ttk.Button(t2_frm4, text=lang['Add to download list'],
                   command=lambda: gui.add_to_list([gui.id_box.get(), ])).pack(padx=45, pady=5, side='left')

        gui.dl_size_lbl = ttk.Label(t2_frm12, text=lang['Size:']+',', font='Helvetica 10 bold')
        gui.dl_size_lbl.pack(side='left', padx=15)
        ttk.Label(t2_frm12, text=lang['Online ticket:'], font='Helvetica 10 bold').pack(side='left', padx=5)
        gui.has_ticket_lbl = ttk.Label(t2_frm12, text='', font='Helvetica 10 bold')
        gui.has_ticket_lbl.pack(side='left')
        ttk.Label(t2_frm6, text=lang['Download list:'], font='Helvetica 10 bold').pack(pady=7)
        dl_scroller = ttk.Scrollbar(t2_frm3, orient='vertical')
        dl_scroller.pack(side='right', fill='y')
        gui.dl_listbox = Listbox(t2_frm3)
        gui.dl_listbox.pack(side='right', fill='both', expand=True)
        gui.dl_listbox.config(yscrollcommand=dl_scroller.set)
        dl_scroller.config(command=gui.dl_listbox.yview)
        ttk.Button(t2_frm7, text=lang['Remove selected'], command=gui.remove_from_list).pack(padx=3, pady=2, side='left',
                                                                                        anchor='w')
        ttk.Button(t2_frm7, text=lang['Clear list'], command=gui.clear_list).pack(padx=3, pady=2, side='left')
        ttk.Label(t2_frm8, text='', textvariable=gui.total_dl_size, font='Helvetica 10 bold').pack(side='left')
        ttk.Label(t2_frm10, text='', textvariable=gui.total_dl_size_warning, foreground='red').pack(side='left')
        gui.download_button = ttk.Button(t2_frm11, text=lang['Download'].upper(), width=25, command=gui.download_clicked)
        gui.download_button.pack(padx=5, pady=10, side='right')

        t2_frm0.grid(row=0, column=1, columnspan=6, sticky='w')
        t2_frm1.grid(row=1, column=1, columnspan=3, sticky='w')
        t2_frm2.grid(row=2, column=1, columnspan=5, sticky='w')
        t2_frm3.grid(row=3, column=1, columnspan=6, rowspan=3, sticky='nsew')
        t2_frm4.grid(row=7, column=1, columnspan=2, sticky='w')
        t2_frm5.grid(row=8, column=1, columnspan=3, sticky='w')
        t2_frm6.grid(row=3, column=4, sticky='nw')
        t2_frm7.grid(row=6, column=5, columnspan=1, sticky='e')
        t2_frm8.grid(row=6, column=3, sticky='w', columnspan=2)
        t2_frm9.grid(row=6, column=1, sticky='w')
        t2_frm10.grid(row=9, column=3, columnspan=3, sticky='ne')
        t2_frm11.grid(row=7, column=5, sticky='e', padx=5)
        t2_frm12.grid(row=9, column=1, columnspan=2, sticky='w')


