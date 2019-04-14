try:
    import ttk
    from Tkinter import Listbox, Scale
except ImportError:
    from tkinter import ttk, Listbox, Scale

from modules.custom.ACOWD_mod import __VERSION__ as fnku_version



class UpdatesTab(ttk.Frame):
    def __init__(self, master=None, gui=None):
        ttk.Frame.__init__(self, master=master)
        lang = gui.get_gui_language()
        
        t4_frm0 = ttk.Frame(self)
        t4_frm1 = ttk.Frame(self)
        t4_frm2 = ttk.Frame(self)
        t4_frm3 = ttk.Frame(self)
        t4_frm4 = ttk.Frame(self)
        t4_frm5 = ttk.Frame(self)
        t4_frm6 = ttk.Frame(self)
        t4_frm7 = ttk.Frame(self)
        t4_frm8 = ttk.Frame(self)
        t4_frm9 = ttk.Frame(self)
        t4_frm10 = ttk.Frame(self)
        t4_frm11 = ttk.Frame(self)

        ttk.Label(t4_frm0, text=lang['Version Information:']+'\n').pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm1, text='GUI ' + lang['application:'], font="Helvetica 13 bold").pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm2, text=lang['Running version:']+'\n'+lang['Targeted for:']).pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm2, text=gui.runningversion + '\n' + gui.targetversion).pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm3, text=lang['Latest release:']).pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm3, textvariable=gui.newest_gui_ver).pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm4, text=lang['Update to latest release:']).pack(padx=5, pady=1, side='left')
        ttk.Button(t4_frm4, text=lang['Update-verb'],
                   command=lambda: gui.update_application('gui', gui.versions['gui_new'])).pack(padx=5, pady=1,
                                                                                                  side='left')

        ttk.Label(t4_frm7, text='ACOWD ' + lang['application:'], font="Helvetica 13 bold").pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm8, text=lang['Running version:']).pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm8, text=fnku_version).pack(padx=5, pady=1, side='left')

        t4_frm0.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        t4_frm1.grid(row=1, column=1, padx=5, sticky='w')
        t4_frm2.grid(row=2, column=1, padx=25, sticky='w')
        t4_frm3.grid(row=3, column=1, padx=25, sticky='w')
        t4_frm4.grid(row=4, column=1, padx=25, sticky='w')
        t4_frm5.grid(row=5, column=1, padx=25, sticky='w')
        t4_frm6.grid(row=6, column=1, padx=5, sticky='w')
        t4_frm7.grid(row=7, column=1, padx=5, sticky='w')
        t4_frm8.grid(row=8, column=1, padx=25, sticky='w')
        t4_frm9.grid(row=9, column=1, padx=25, sticky='w')
        t4_frm10.grid(row=10, column=1, padx=25, sticky='w')
        t4_frm11.grid(row=11, column=1, padx=25, sticky='w')

