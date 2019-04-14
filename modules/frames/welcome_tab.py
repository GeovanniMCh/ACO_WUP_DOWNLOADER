try:
    import ttk
    from Tkinter import PhotoImage
except ImportError:
    from tkinter import ttk
    from tkinter import PhotoImage
    
import os



class WelcomeTab(ttk.Frame):
    def __init__(self, master=None, gui=None):
        ttk.Frame.__init__(self, master=master)
        lang = gui.get_gui_language()
        
        t1_frm1 = ttk.Frame(self)
        t1_frm2 = ttk.Frame(self)
        t1_frm3 = ttk.Frame(self)
        t1_frm4 = ttk.Frame(self)
        t1_frm5 = ttk.Frame(self)
        t1_frm6 = ttk.Frame(self)

        self.img = PhotoImage(file=os.path.join('images', 'logo.ppm'))
        ttk.Label(t1_frm1, image=self.img).pack()
        ttk.Label(t1_frm2, justify='center',
                  text=lang[('This is a simple GUI by dojafoja.\nCredits to cearp,'
                             'cerea1killer,GeovanniMCh and all the Github contributors for writing Aco Wup Downloader.')]).pack()

        ttk.Label(t1_frm3, justify='center',
                  text=lang[('If this is your first time running the program, you will need to provide the name'
                             ' of *that key site*. If you haven\'t already\nprovided the address to the key site,'
                             ' you MUST provide it below before proceeding. You only need to provide this information'
                             ' once!')]).pack(pady=15)

        gui.enterkeysite_lbl = ttk.Label(t1_frm4, text=lang[('Enter the name of *that key site*. Remember '
                                                              'that you MUST include the http:// or https://')])
        gui.enterkeysite_lbl.pack(pady=15, side='left')
        gui.http_lbl = ttk.Label(t1_frm5, text='')
        gui.http_lbl.pack(pady=15, side='left')
        gui.keysite_box = ttk.Entry(t1_frm5, width=40, style="EntryStyle.TEntry")
        gui.keysite_box.pack(pady=15, side='left')
        gui.submitkeysite_btn = ttk.Button(t1_frm6, text=lang['submit'], command=gui.submit_key_site)
        gui.submitkeysite_btn.pack()
        gui.updatelabel = ttk.Label(t1_frm6, text='')
        gui.updatelabel.pack(pady=15)

        t1_frm1.pack()
        t1_frm2.pack()
        t1_frm3.pack()
        t1_frm4.pack()
        t1_frm5.pack()
        t1_frm6.pack()

