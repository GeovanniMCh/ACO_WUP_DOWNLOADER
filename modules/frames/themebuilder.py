try:
    from Tkinter import StringVar
    import ttk
    import tkColorChooser as chooser
except ImportError:
    from tkinter import ttk, StringVar
    from tkinter import colorchooser as chooser
    
import os

# This is a ttk.Frame subclass that is used by FunKii-UI and packed into a tkinter.Toplevel widget.
# It is used when displaying the theme builder window.
class Root(ttk.Frame):
    def __init__(self, app=None, master=None):
        global gui
        global user_theme_name
        gui = app
        
        ttk.Frame.__init__(self, master=master)
        self.user_theme_name = StringVar()

        t2_f1 = ttk.Frame(self)
        t2_f2 = ttk.Frame(self)
        t2_f3 = ttk.Frame(self)
        t2_f4 = ttk.Frame(self)
        t2_f5 = ttk.Frame(self)
        t2_f6 = ttk.Frame(self)
        t2_f7 = ttk.Frame(self)
        t2_f8 = ttk.Frame(self)
        t2_f9 = ttk.Frame(self)
        t2_f10 = ttk.Frame(self)
        t2_f11 = ttk.Frame(self)
        t2_f12 = ttk.Frame(self)
        t2_f13 = ttk.Frame(self)
        t2_f14 = ttk.Frame(self)

        ttk.Label(t2_f1, text=lang['Main:']).pack(side='left', padx=15, pady=5)
        ttk.Button(t2_f1, text=lang['choose color'], command=lambda: self.getusercolor('main')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f2, text=lang['Main Text:']).pack(side='left', padx=15)
        ttk.Button(t2_f2, text=lang['choose color'], command=lambda: self.getusercolor('maintext')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f3, text=lang['Entry/List Box:']).pack(side='left', padx=15)
        ttk.Button(t2_f3, text=lang['choose color'], command=lambda: self.getusercolor('box')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f4, text=lang['Entry/List Box Text:']).pack(side='left', padx=15)
        ttk.Button(t2_f4, text=lang['choose color'], command=lambda: self.getusercolor('boxtext')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f5, text=lang['The theme options below do not work on Windows']).pack(padx=15, pady=15, side='left')
        ttk.Label(t2_f6, text=lang['Button:']).pack(side='left', padx=15)
        ttk.Button(t2_f6, text=lang['choose color'], command=lambda: self.getusercolor('button')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f7, text=lang['Button Text:']).pack(side='left', padx=15)
        ttk.Button(t2_f7, text=lang['choose color'], command=lambda: self.getusercolor('buttontext')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f8, text=lang['Button on hover:']).pack(side='left', padx=15)
        ttk.Button(t2_f8, text=lang['choose color'], command=lambda: self.getusercolor('buttonhover')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f9, text=lang['Button Text on hover:']).pack(side='left', padx=15)
        ttk.Button(t2_f9, text=lang['choose color'], command=lambda: self.getusercolor('buttontexthover')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f10, text=lang['Tab:']).pack(side='left', padx=15)
        ttk.Button(t2_f10, text=lang['choose color'], command=lambda: self.getusercolor('tab')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f11, text=lang['Tab text:']).pack(side='left', padx=15)
        ttk.Button(t2_f11, text=lang['choose color'], command=lambda: self.getusercolor('tabtext')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f12, text=lang['Tab on hover:']).pack(side='left', padx=15)
        ttk.Button(t2_f12, text=lang['choose color'], command=lambda: self.getusercolor('tabhover')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f13, text=lang['Tab text on hover:']).pack(side='left', padx=15)
        ttk.Button(t2_f13, text=lang['choose color'], command=lambda: self.getusercolor('tabtexthover')).pack(side='left', padx=15, pady=5)
        ttk.Label(t2_f14, text=lang['Save this theme:'], font='Helvetica 13 bold').pack(side='top', anchor='w', padx=15, pady=10)
        ttk.Label(t2_f14, text=lang['Theme name:']).pack(side='left', padx=15)
        ttk.Entry(t2_f14, textvariable=self.user_theme_name, width=35, style="EntryStyle.TEntry").pack(side='left', padx=10)
        ttk.Button(t2_f14, text=lang['Save theme'], command=self.save_theme).pack(side='left', padx=15)
        

        t2_f1.pack(anchor='w', side='top')
        t2_f2.pack(anchor='w', side='top')
        t2_f3.pack(anchor='w', side='top')
        t2_f4.pack(anchor='w', side='top')
        t2_f5.pack(anchor='w', side='top', fill='x', expand=True)
        t2_f6.pack(anchor='w', side='top')
        t2_f7.pack(anchor='w', side='top')
        t2_f8.pack(anchor='w', side='top')
        t2_f9.pack(anchor='w', side='top')
        t2_f10.pack(anchor='w', side='top')
        t2_f11.pack(anchor='w', side='top')
        t2_f12.pack(anchor='w', side='top')
        t2_f13.pack(anchor='w', side='top')
        t2_f14.pack(anchor='w', side='top',pady=30)

        self.pack()



    def getusercolor(self, category):
        for i in ('main', 'maintext', 'box', 'boxtext', 'button', 'buttontext', 'buttonhover', 'buttontexthover',
                  'tab', 'tabtext', 'tabhover', 'tabtexthover'):
            if i == category:
                choice = chooser.askcolor(theme_record.get(i, None))[1]
                if choice:
                    theme_record[i] = choice
                break
        
        gui.set_theme(theme_record)
        self.focus_set()


    def save_theme(self):
        gui.save_custom_theme(self.user_theme_name.get(), theme_record)
        self.focus_set()

def rgb_to_hex(rgb):
    if rgb.startswith("("):
        rgb = eval(rgb)
        rgb = "#%02x%02x%02x" % rgb

    return rgb

def set_record(record):
    global theme_record
    for i in record:
        record[i] = rgb_to_hex(record[i])
        
    theme_record = record

        
theme_record = {}
#gui = None
#lang = None
        
