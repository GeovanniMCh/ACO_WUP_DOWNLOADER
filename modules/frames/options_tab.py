try:
    import ttk
    from Tkinter import Listbox, Scale
except ImportError:
    from tkinter import ttk, Listbox, Scale



class OptionsTab(ttk.Frame):
    def __init__(self, master=None, gui=None):
        ttk.Frame.__init__(self, master=master)
        lang = gui.get_gui_language()
        
        t3_frm1 = ttk.Frame(self)
        t3_frm2 = ttk.Frame(self)
        t3_frm3 = ttk.Frame(self)
        t3_frm4 = ttk.Frame(self)
        t3_frm5 = ttk.Frame(self)
        t3_frm6 = ttk.Frame(self)
        t3_frm7 = ttk.Frame(self)
        t3_frm8 = ttk.Frame(self)
        t3_frm9 = ttk.Frame(self)
        gui.t3_frm10 = ttk.Frame(self)
        t3_frm11 = ttk.Frame(self)
        t3_frm12 = ttk.Frame(self)
        t3_frm13 = ttk.Frame(self)
        t3_frm14 = ttk.Frame(self)
        t3_frm15 = ttk.Frame(self)
        gui.t3_frm16 = ttk.Frame(self)
        t3_frm17 = ttk.Frame(self)
        t3_frm18 = ttk.Frame(self)
        t3_frm19 = ttk.Frame(self)
        t3_frm20 = ttk.Frame(self)
        t3_frm21 = ttk.Frame(self)
        
        ttk.Label(t3_frm1, text=lang['Output directory:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        gui.out_dir_box = ttk.Entry(t3_frm1, width=35, textvariable=gui.output_dir, style="EntryStyle.TEntry")
        gui.out_dir_box.pack(padx=5, pady=4, side='left')
        ttk.Button(t3_frm1, text=lang['Browse'], command=gui.get_output_directory).pack(padx=5, pady=3, side='left')
        ttk.Label(t3_frm2, text=lang['Retry count:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        gui.retry_count_box = ttk.Combobox(t3_frm2, state='readonly', width=5, values=[i for i in range(10)],
                                            textvariable=gui.retry_count)
        gui.retry_count_box.set(3)
        gui.retry_count_box.pack(padx=5, pady=4, side='left')
        ttk.Label(t3_frm3, text=lang['Patch demo play limit:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        gui.patch_demo_true = ttk.Radiobutton(t3_frm3, text=lang['Yes'], variable=gui.patch_demo, value=True)
        gui.patch_demo_false = ttk.Radiobutton(t3_frm3, text=lang['No'], variable=gui.patch_demo, value=False)
        gui.patch_demo_true.pack(padx=5, pady=3, side='left')
        gui.patch_demo_false.pack(padx=5, pady=3, side='left')
        ttk.Label(t3_frm4, text=lang['Patch DLC:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        gui.patch_dlc_true = ttk.Radiobutton(t3_frm4, text=lang['Yes'], variable=gui.patch_dlc, value=True)
        gui.patch_dlc_false = ttk.Radiobutton(t3_frm4, text=lang['No'], variable=gui.patch_dlc, value=False)
        gui.patch_dlc_true.pack(padx=5, pady=3, side='left')
        gui.patch_dlc_false.pack(padx=5, pady=3, side='left')
        ttk.Label(t3_frm5, text=lang['Tickets only mode:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        gui.tickets_only_true = ttk.Radiobutton(t3_frm5, text=lang['On'], variable=gui.tickets_only, value=True)
        gui.tickets_only_false = ttk.Radiobutton(t3_frm5, text=lang['Off'], variable=gui.tickets_only, value=False)
        gui.tickets_only_true.pack(padx=5, pady=3, side='left')
        gui.tickets_only_false.pack(padx=5, pady=3, side='left')
        ttk.Label(t3_frm7, text=lang['Choose your preferred download behavior:'], font='Helvetica 10 bold').pack(padx=15,
                                                                                                           pady=3,
                                                                                                           side='left')

        ttk.Radiobutton(t3_frm8, text=lang[(
            'Download legit tickets for titles when available and generate fake tickets for titles that do '
            'not have legit tickets')], variable=gui.dl_behavior, value=1).pack(padx=5,pady=3,side='left')
                                                                                                             
        ttk.Radiobutton(t3_frm9, text=lang['Generate fake tickets for all titles except updates, even if a legit ticket exists.'],
                        variable=gui.dl_behavior, value=2).pack(padx=5, pady=3, side='left')
                                                                                              

        ttk.Label(t3_frm11, text=lang['Auto-fetch game updates and dlc:'], font='Helvetica 10 bold').pack(padx=15, pady=3,
                                                                                                    side='left')

        ttk.Label(t3_frm12, text=lang[('When adding games to the download list, you can automatically fetch it\'s '
                                       'related update and dlc.')]).pack(padx=5, side='left')

        ttk.Radiobutton(t3_frm13, text=lang['Disabled'], variable=gui.auto_fetching, value='disabled',
                        command=gui.toggle_widgets).pack(padx=5, pady=3, side='left')

        ttk.Radiobutton(t3_frm14, text=lang['Prompt for content to fetch'], variable=gui.auto_fetching,
                        value='prompt', command=gui.toggle_widgets).pack(padx=5, pady=3, side='left')

        ttk.Radiobutton(t3_frm15, text=lang['Automatically fetch content:'], variable=gui.auto_fetching, value='auto',
                        command=gui.toggle_widgets).pack(padx=5, pady=3, side='left')

        ttk.Checkbutton(gui.t3_frm16, text=lang['Fetch game updates'], variable=gui.fetch_updates).pack(padx=15, pady=3,
                                                                                                    side='left')

        ttk.Checkbutton(gui.t3_frm16, text=lang['Fetch game dlc'], variable=gui.fetch_dlc).pack(padx=5, pady=3, side='left')

        ttk.Label(t3_frm17, text=lang['Number of threads to use when downloading:'], font='Helvetica 10 bold').pack(
            side='left', padx=15, pady=3)

        gui.throttler = Scale(t3_frm17, from_=1, to=5, length=200, tickinterval=1, orient='horizontal',
                                  variable=gui.total_thread_count)
        gui.throttler.pack(side='left', pady=3)

        ttk.Label(t3_frm18, text=lang['Download titlekeys.json every time the program starts:'], font='Helvetica 10 bold').pack(padx=15,
                                                                                                                          pady=3,
                                                                                                                          side='left')
        
        ttk.Radiobutton(t3_frm18, text=lang['Yes'], variable=gui.download_data_on_start, value=True).pack(padx=10, pady=3, side='left')
        ttk.Radiobutton(t3_frm18, text=lang['No'], variable=gui.download_data_on_start, value=False).pack(padx=10, pady=3, side='left')
        ttk.Button(t3_frm18, text=lang['Download'], command=lambda: gui.populate_selection_list(download_data=True)).pack(padx=10, pady=3, side='left')
        ttk.Label(t3_frm19, text=lang['Select your language:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        ttk.Radiobutton(t3_frm19, text=lang['English'], variable=gui.language, value='english').pack(padx=10, pady=3, side='left')
        ttk.Radiobutton(t3_frm19, text=lang['Spanish'], variable=gui.language, value='spanish').pack(padx=10, pady=3, side='left')
        ttk.Label(t3_frm20, text=lang['Select your theme:'], font='Helvetica 10 bold').pack(padx=15, pady=3, side='left')
        foo = [i for i in gui.themes]
        foo.sort()
        gui.theme_selector = ttk.Combobox(t3_frm20, values=foo, width=30, textvariable = gui.selected_theme)
        gui.theme_selector.pack(padx=10,pady=3, side='left')
        ttk.Button(t3_frm20, text=lang["Create custom theme"], command=gui.show_theme_frame).pack(padx=10, pady=3, side='left')
        
        ttk.Button(t3_frm21, text=lang['Save as my settings'], width=20, command=gui.save_settings).pack(padx=10, pady=3,
                                                                                                          side='left')
        ttk.Button(t3_frm21, text=lang['Reset settings'], width=20, command=lambda: gui.load_settings(reset=True)).pack(
                   padx=10, pady=3, side='left')
            
        t3_frm1.grid(row=1, column=1, sticky='w')
        t3_frm2.grid(row=2, column=1, sticky='w')
        t3_frm3.grid(row=3, column=1, sticky='w')
        t3_frm4.grid(row=4, column=1, sticky='w')
        t3_frm5.grid(row=5, column=1, sticky='w')
        #t3_frm6.grid(row=6, column=1, sticky='w')
        t3_frm7.grid(row=7, column=1, sticky='w')
        t3_frm8.grid(row=8, column=1, padx=40, sticky='w')
        t3_frm9.grid(row=9, column=1, padx=40, sticky='w')
        gui.t3_frm10.grid(row=10, column=1, padx=80, sticky='w')
        t3_frm11.grid(row=11, column=1, sticky='w')
        t3_frm12.grid(row=12, column=1, padx=40, sticky='w')
        t3_frm13.grid(row=13, column=1, padx=40, sticky='w')
        t3_frm14.grid(row=14, column=1, padx=40, sticky='w')
        t3_frm15.grid(row=15, column=1, padx=40, sticky='w')
        gui.t3_frm16.grid(row=16, column=1, padx=80, sticky='w')
        t3_frm17.grid(row=17, column=1, sticky='w')
        t3_frm18.grid(row=18, column=1, sticky='w')
        t3_frm19.grid(row=19, column=1, sticky='w')
        t3_frm20.grid(row=20, column=1, sticky='w')
        t3_frm21.grid(row=21, column=1, padx=10, pady=20, sticky='w')

