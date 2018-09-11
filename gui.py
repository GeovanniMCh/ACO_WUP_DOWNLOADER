#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:  # Python 2 imports
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as message
    from HTMLParser import HTMLParser
    from Tkinter import Image
    from urllib2 import urlopen, URLError, HTTPError
    from Queue import Queue

except ImportError:  # Python 3 imports
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox as message
    from html.parser import HTMLParser
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
    from queue import Queue

import os
import json
import zipfile
from distutils.version import LooseVersion
import binascii
import sys
import sqlite3
import time
import threading
from datetime import datetime

try:
    import alucardianos_wup_helper as fnku
except ImportError:
    fnku = None

__VERSION__ = "1.0.4"
targetversion = "alucardianos wup helper"
current_gui = LooseVersion(__VERSION__)
PhotoImage = tk.PhotoImage
DEBUG = False
failed_downloads = []
JOBQ = Queue()
RESULTQ = Queue()

try:
    fnku_VERSION_ = str(fnku.__VERSION__)
    current_fnku = LooseVersion(fnku_VERSION_)
except:
    fnku__VERSION__ = "?"
    current_fnku = LooseVersion('0')



class VersionParser(HTMLParser):
    fnku_data_set = []
    gui_data_set = []

    def handle_starttag(self, tag, attrs):
        fnku_data_set = []
        gui_data_set = []
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if value.startswith("/llakssz") and value.endswith(".zip"):
                        self.fnku_data_set.append(value)
                    elif value.startswith("/GeovanniMCh") and value.endswith(".zip"):
                        self.gui_data_set.append(value)


class DownloadSession():
    def __init__(self, jobQ, resultQ, threadcount):
        self.threads = []
        self.jobQ = jobQ
        self.resultQ = resultQ
        self.threadcount = threadcount

        for i in range(1, threadcount + 1):
            self.threads.append(DownloadWorker(jobQ, resultQ, str(i)))

    def start_session(self):
        for i in self.threads:
            i.start()

    def populate_job(self, joblist):
        for i in joblist:
            for job in i:
                self.jobQ.put(job)

    def poison_threads(self):
        for i in range(self.threadcount):
            self.jobQ.put(None)  # A poison pill to kill each thread


# A Multithread download 'worker'. Using threads should improve download speeds but may
# cause servers to drop the connection with an 'Error 104, Connection reset by peer'
# when too many threads are downloading at once. More testing is needed to determine an
# optimum number of concurrent downloads.
class DownloadWorker(threading.Thread):
    def __init__(self, jobQ, resultQ, thread_id):
        threading.Thread.__init__(self)
        self.jobQ = jobQ
        self.resultQ = resultQ
        self.daemon = True
        self.thread_id = thread_id

    def run(self):
        while True:
            if not self.jobQ.empty():
                job = self.jobQ.get()
                if not job:
                    self.resultQ.put(('status', self.thread_id, 'Finished'))
                    self.resultQ.put(('log', 'Thread {} has terminated'.format(self.thread_id)))
                    self.resultQ.put(('thread died', ''))
                    break

                else:
                    title_id = job[0][4]
                    if title_id in failed_downloads:
                        self.resultQ.put(('progress', job[0][3]))
                        continue

                    app = job[0]
                    h3 = job[1]

                    # Attempt to download .app file
                    if not fnku.download_file(app[0], app[1], app[2], expected_size=app[3], resultsq=self.resultQ,
                                              titleid=title_id, threadid=self.thread_id):
                        self.resultQ.put(('fail', '{}.app'.format(app[0].split('/')[6]), title_id))
                        self.resultQ.put(('log', 'DOWNLOAD ERROR: Thread {} failed to download {}.app for title {}'.format(
                            self.thread_id, app[0].split('/')[6], title_id, title_id)))
                    else:
                        self.resultQ.put(
                            ('log', 'Thread {} finished downloading {}.app for title {}'.format(self.thread_id, app[0].split('/')[6], title_id)))

                    # Attempt to download .h3 file
                    if not fnku.download_file(h3[0], h3[1], h3[2], ignore_404=h3[3], resultsq=self.resultQ,
                                              titleid=title_id, threadid=self.thread_id):
                        self.resultQ.put(('fail', '{}'.format(h3[0].split('/')[6]), title_id))
                        self.resultQ.put(('log', 'DOWNLOAD ERROR: Thread {} failed to download {} for title {}'.format(
                            self.thread_id, h3[0].split('/')[6], title_id)))
                    else:
                        self.resultQ.put(
                            ('log', 'Thread {} finished downloading {} for title {}'.format(self.thread_id, h3[0].split('/')[6], title_id)))


class RootWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)
        self.versions = {'gui_new': '', 'gui_all': '', 'gui_url': 'https://github.com/GeovanniMCh/ALUCARDIANOS-WUP-HELPER/releases',
                         'fnku_new': '', 'fnku_all': '',
                         'fnku_url': 'https://github.com/llakssz/FunKiiU/releases'}

        self.download_list = []
        self.selection_list = []
        self.title_data = []
        self.nb = ttk.Notebook(self)
        tab1 = ttk.Frame(self.nb)
        self.tab2 = ttk.Frame(self.nb)
        self.tab2.rowconfigure(3, weight=2)
        self.tab2.columnconfigure(1, weight=2)
        self.tab2.rowconfigure(3, weight=2)
        self.tab2.columnconfigure(4, weight=2)
        tab3 = ttk.Frame(self.nb)
        tab4 = ttk.Frame(self.nb)
        self.tab5 = ttk.Frame(self.nb)
        self.tab5.rowconfigure(22, weight=2)
        self.tab5.columnconfigure(1, weight=2)
        self.tab5.rowconfigure(7, weight=2)
        self.tab5.columnconfigure(5, weight=2)
        self.nb.add(tab1, text="Inicio")
        self.nb.add(self.tab2, text="Descargas")
        self.nb.add(self.tab5, text="Progreso")		
        self.nb.add(tab3, text="Opciones")
        self.nb.add(tab4, text="Actualizaciones")
        self.nb.pack(fill="both", expand=True)
        self.output_dir = tk.StringVar()
        self.retry_count = tk.IntVar(value=3)
        self.patch_demo = tk.BooleanVar(value=True)
        self.patch_dlc = tk.BooleanVar(value=True)
        self.tickets_only = tk.BooleanVar(value=False)
        self.simulate_mode = tk.BooleanVar(value=False)
        self.filter_usa = tk.BooleanVar(value=True)
        self.filter_eur = tk.BooleanVar(value=True)
        self.filter_jpn = tk.BooleanVar(value=True)
        self.filter_game = tk.BooleanVar(value=True)
        self.filter_dlc = tk.BooleanVar(value=True)
        self.filter_update = tk.BooleanVar(value=True)
        self.filter_demo = tk.BooleanVar(value=True)
        self.filter_system = tk.BooleanVar(value=True)
        self.filter_hasticket = tk.BooleanVar(value=False)
        self.show_batch = tk.BooleanVar(value=False)
        self.dl_behavior = tk.IntVar(value=1)
        self.fetch_dlc = tk.BooleanVar(value=True)
        self.fetch_updates = tk.BooleanVar(value=True)
        self.remove_ignored = tk.BooleanVar(value=True)
        self.auto_fetching = tk.StringVar(value='prompt')
        self.fetch_on_batch = tk.BooleanVar(value=False)
        self.batch_op_running = tk.BooleanVar(value=False)
        self.total_dl_size = tk.StringVar(value='Tamaño total:')
        self.total_dl_size_warning = tk.StringVar()
        self.dl_progress = 0
        self.dl_progress_string = tk.StringVar()
        self.dl_progress_string.set('0')
        self.dl_total_string = tk.StringVar()
        self.dl_total_string.set('0')
        self.dl_total_float = 0
        self.dl_percentage_string = tk.StringVar()
        self.dl_percentage_string.set('0.00%')
        self.dl_speed = tk.StringVar()
        self.active_thread_count = 0
        self.thread1_status = tk.StringVar()
        self.thread2_status = tk.StringVar()
        self.thread3_status = tk.StringVar()
        self.thread4_status = tk.StringVar()
        self.thread5_status = tk.StringVar()
        self.total_thread_count = tk.IntVar()
        self.dl_warning_msg = "! Tiene uno o más elementos en la lista con un tamaño desconocido.\nEsto puede significar que el título no está disponible."
        self.idvar = tk.StringVar()
        self.idvar.trace('w', self.id_changed)
        self.newest_gui_ver = tk.StringVar()
        self.newest_fnku_ver = tk.StringVar()
        self.user_search_var = tk.StringVar()
        self.user_search_var.trace('w', self.user_search_changed)
        self.usa_selections = {'game': [], 'dlc': [], 'update': [], 'demo': [], 'system': []}
        self.eur_selections = {'game': [], 'dlc': [], 'update': [], 'demo': [], 'system': []}
        self.jpn_selections = {'game': [], 'dlc': [], 'update': [], 'demo': [], 'system': []}
        self.title_sizes_raw = {}
        self.title_sizes = {}
        self.reverse_title_names = {}
        self.title_dict = {}
        self.has_ticket = []
        self.errors = 0

        # Tab 1
        t1_frm1 = ttk.Frame(tab1)
        t1_frm2 = ttk.Frame(tab1)
        t1_frm3 = ttk.Frame(tab1)
        t1_frm4 = ttk.Frame(tab1)
        t1_frm5 = ttk.Frame(tab1)
        t1_frm6 = ttk.Frame(tab1)

        self.img = PhotoImage(file='logo.ppm')
        ttk.Label(t1_frm1, image=self.img).pack()
        ttk.Label(t1_frm2, justify='center',
                  text=('Esta es una GUI simple de [Alucardio Comunidad Oficial] que está escrita para *Alucardianos Wup Helper*.\nCreditos a GeovanniMCh ,'
                        ' Alucardio y a todos los contribuidores de www.alucardianos.com.')).pack()
        
        ttk.Label(t1_frm3, justify='center',
                  text=('Si esta es la primera vez que abres este programa, necesitaras ingresar el nombre'
                        ' de *la pagina de Tickets*. \nSi áun no has ingresado la dirección de *la pagina de Tickets*,'
                        ' debes proveerla antes de continuar. \nSolo necesitas hacer esto una vez!.')).pack(pady=15)
        
        self.enterkeysite_lbl = ttk.Label(t1_frm4, text=('Escribe el nombre de *la pagina de Tickets*. Recuerda '
                                                         'que debe de incluir http:// o https://'))
        self.enterkeysite_lbl.pack(pady=15, side='left')
        self.http_lbl = ttk.Label(t1_frm5, text='')
        self.http_lbl.pack(pady=15, side='left')
        self.keysite_box = ttk.Entry(t1_frm5, width=40)
        self.keysite_box.pack(pady=15, side='left')
        self.submitkeysite_btn = ttk.Button(t1_frm6, text='ACEPTAR', command=self.submit_key_site)
        self.submitkeysite_btn.pack()
        self.updatelabel = ttk.Label(t1_frm6, text='')
        self.updatelabel.pack(pady=15)

        t1_frm1.pack()
        t1_frm2.pack()
        t1_frm3.pack()
        t1_frm4.pack()
        t1_frm5.pack()
        t1_frm6.pack()

        ## Check for FunKiiU existence and download targeted version if not.
        global fnku
        if not fnku:
            self.set_icon()
            message.showinfo('Falta ALUCARDIANOS WUP HELPER', 'Hace falta ALUCARDIANOS WUP HELPER. Lo descargaremos para ti.',
                             parent=self)
            self.update_application('fnku', targetversion.split('v')[1])
            import FunKiiU as fnku
            global current_fnku
            current_fnku = LooseVersion(str(fnku.__VERSION__))
            message.showinfo('Listo', 'ALUCARDIANOS WUP HELPER ha sido descargado para ti. ¡Disfrutar!', parent=self)

        # Tab2
        t2_frm0 = ttk.Frame(self.tab2)
        t2_frm1 = ttk.Frame(self.tab2)
        t2_frm2 = ttk.Frame(self.tab2)
        t2_frm3 = ttk.Frame(self.tab2)
        t2_frm4 = ttk.Frame(self.tab2)
        t2_frm5 = ttk.Frame(self.tab2)
        t2_frm6 = ttk.Frame(self.tab2)
        t2_frm7 = ttk.Frame(self.tab2)
        t2_frm8 = ttk.Frame(self.tab2)
        t2_frm9 = ttk.Frame(self.tab2)
        t2_frm10 = ttk.Frame(self.tab2)
        t2_frm11 = ttk.Frame(self.tab2)
        t2_frm12 = ttk.Frame(self.tab2)
        t2_frm13 = ttk.Frame(self.tab2)
        t2_frm14 = ttk.Frame(self.tab2)
        t2_frm15 = ttk.Frame(self.tab2)
        t2_frm16 = ttk.Frame(self.tab2)

        ttk.Label(t2_frm0,
                  text=('*.Introduzca el número de Title ID que desee en la lista. \n*.Utilice el cuadro de búsqueda para filtrar los títulos que contienen'
                        ' su término de búsqueda. \n*.También puede introducir un Title ID manualmente.')).pack(padx=5, pady=16)                                                                                                                                                                                           
        ttk.Label(t2_frm1, text='Elija regiones para mostrar:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')                                                                                         
        ttk.Checkbutton(t2_frm1, text='USA', variable=self.filter_usa,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')      
        ttk.Checkbutton(t2_frm1, text='EUR', variable=self.filter_eur,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                                                 
        ttk.Checkbutton(t2_frm1, text='JPN', variable=self.filter_jpn,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                                                     
        ttk.Label(t2_frm2, text='Elija contenido para mostrar:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')                                                                                           
        ttk.Checkbutton(t2_frm2, text='Game', variable=self.filter_game,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                              
        ttk.Checkbutton(t2_frm2, text='Update', variable=self.filter_update,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                                      
        ttk.Checkbutton(t2_frm2, text='DLC', variable=self.filter_dlc,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                                    
        ttk.Checkbutton(t2_frm2, text='Demo', variable=self.filter_demo,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                                                     
        ttk.Checkbutton(t2_frm2, text='System', variable=self.filter_system,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                                                                                                                           
        ttk.Checkbutton(t2_frm2, text='Mostrar solo titulos con un ticket legítimo', variable=self.filter_hasticket,
                        command=lambda: self.populate_selection_list(download_data=False)).pack(padx=5, pady=5, side='left')                                                                                                            
        ttk.Label(t2_frm3, text='Selección:', font='Helvetica 10 bold').pack(padx=15, pady=7, side='top', anchor='w')
                                                                                   
        sel_scroller = ttk.Scrollbar(t2_frm3, orient='vertical')
        self.selection_box = tk.Listbox(t2_frm3)
        self.selection_box.pack(side='left', fill='both', expand=True)
        sel_scroller.pack(side='left', fill='y')
        self.selection_box.config(yscrollcommand=sel_scroller.set)
        sel_scroller.config(command=self.selection_box.yview)
        self.selection_box.bind('<<ListboxSelect>>', self.selection_box_changed)
        self.selection_box.bind('<<Up>>', self.selection_box_changed)
        ttk.Label(t2_frm9, text='Buscar:', font='Helvetica 10 bold').pack(padx=15, pady=7, side='left')
        ttk.Entry(t2_frm9, width=30, textvariable=self.user_search_var).pack(side='left')
        ttk.Label(t2_frm4, text='Title ID:', font='Helvetica 10 bold').pack(padx=15, pady=7, side='left')
        self.id_box = ttk.Entry(t2_frm4, width=20, textvariable=self.idvar)
        self.id_box.pack(padx=5, pady=5, side='left')
        ttk.Label(t2_frm5, text='Title Key:', font='Helvetica 10 bold').pack(padx=15, pady=7, side='left', anchor='n')
        self.key_box = ttk.Entry(t2_frm5, width=34)
        self.key_box.pack(padx=5, pady=5, side='left')
        ttk.Button(t2_frm4, text='Añadir a la lista de descargas', width=30,
                   command=lambda: self.add_to_list([self.id_box.get(), ])).pack(padx=45, pady=5, side='left')
        self.dl_size_lbl = ttk.Label(t2_frm15, text='Tamaño:,', font='Helvetica 10 bold')
        self.dl_size_lbl.pack(side='left', padx=15)
        ttk.Label(t2_frm15, text='Ticket en línea:', font='Helvetica 10 bold').pack(side='left', padx=5)
        self.has_ticket_lbl = ttk.Label(t2_frm15, text='', font='Helvetica 10 bold')
        self.has_ticket_lbl.pack(side='left')

        ttk.Label(t2_frm6, text='Lista de descargas:', font='Helvetica 10 bold').pack(pady=7)
        dl_scroller = ttk.Scrollbar(t2_frm3, orient='vertical')
        dl_scroller.pack(side='right', fill='y')
        self.dl_listbox = tk.Listbox(t2_frm3)
        self.dl_listbox.pack(side='right', fill='both', expand=True)
        self.dl_listbox.config(yscrollcommand=dl_scroller.set)
        dl_scroller.config(command=self.dl_listbox.yview)
        ttk.Button(t2_frm7, text='Eliminar selección', command=self.remove_from_list).pack(padx=3, pady=2, side='left', anchor='w')                                                                                    
        ttk.Button(t2_frm7, text='Limpiar lista', command=self.clear_list).pack(padx=3, pady=2, side='left')
        ttk.Label(t2_frm8, text='', textvariable=self.total_dl_size, font='Helvetica 10 bold').pack(side='left')
        ttk.Label(t2_frm10, text='', textvariable=self.total_dl_size_warning, foreground='red').pack(side='left')
        ttk.Label(t2_frm11, text='Agregue todas sus selecciones filtradas a la lista:').pack(padx=10, side='left')
        ttk.Button(t2_frm11, text='Añadir todo', command=self.add_filtered_to_list).pack(side='left')
        ttk.Label(t2_frm12, text='Importar trabajo por lotes:').pack(padx=10, side='left')
        ttk.Button(t2_frm12, text='Importar', command=self.batch_import).pack(side='left')
        ttk.Label(t2_frm13, text='Exportar lista actual:').pack(padx=10, side='left')
        ttk.Button(t2_frm13, text='Exportar', command=self.export_to_batch).pack(side='left')
        self.download_button = ttk.Button(t2_frm14, text='DESCARGAR', width=18, command=self.download_clicked)
        self.download_button.pack(padx=5, pady=10, side='right')

        t2_frm0.grid(row=0, column=1, columnspan=6, sticky='w')
        t2_frm1.grid(row=1, column=1, columnspan=3, sticky='w')
        t2_frm2.grid(row=2, column=1, columnspan=5, sticky='w')
        t2_frm3.grid(row=3, column=1, columnspan=6, rowspan=3, sticky='nsew')
        t2_frm4.grid(row=7, column=1, columnspan=2, sticky='w')
        t2_frm5.grid(row=8, column=1, columnspan=3, sticky='w')
        t2_frm6.grid(row=3, column=4, sticky='nw')
        t2_frm7.grid(row=6, column=5, columnspan=1, sticky='e')
        t2_frm8.grid(row=6, column=3, sticky='w',columnspan=2)
        t2_frm9.grid(row=6, column=1, sticky='w')
        t2_frm10.grid(row=9, column=3, columnspan=3, sticky='ne')
        #t2_frm11.grid(row=9, column=1, columnspan=2, sticky='w')
        #t2_frm12.grid(row=10, column=1, columnspan=2, sticky='w')
        #t2_frm13.grid(row=11, column=1, columnspan=2, sticky='w')
        t2_frm14.grid(row=7, column=5, sticky='e', padx=5)
        t2_frm15.grid(row=9, column=1, columnspan=2, sticky='w')
        t2_frm16.grid(row=8, column=5, sticky='e')

        self.batch_frames = (t2_frm11, t2_frm12, t2_frm13)

        # Tab3
        t3_frm1 = ttk.Frame(tab3)
        t3_frm2 = ttk.Frame(tab3)
        t3_frm3 = ttk.Frame(tab3)
        t3_frm4 = ttk.Frame(tab3)
        t3_frm5 = ttk.Frame(tab3)
        t3_frm6 = ttk.Frame(tab3)
        t3_frm7 = ttk.Frame(tab3)
        t3_frm8 = ttk.Frame(tab3)
        t3_frm9 = ttk.Frame(tab3)
        self.t3_frm10 = ttk.Frame(tab3)
        t3_frm11 = ttk.Frame(tab3)
        t3_frm12 = ttk.Frame(tab3)
        t3_frm13 = ttk.Frame(tab3)
        t3_frm14 = ttk.Frame(tab3)
        t3_frm15 = ttk.Frame(tab3)
        self.t3_frm16 = ttk.Frame(tab3)
        t3_frm17 = ttk.Frame(tab3)
        t3_frm18 = ttk.Frame(tab3)

        ttk.Label(t3_frm1, text='Directorio de salida:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
        self.out_dir_box = ttk.Entry(t3_frm1, width=35, textvariable=self.output_dir)
        self.out_dir_box.pack(padx=5, pady=5, side='left')
        ttk.Button(t3_frm1, text='Buscar', command=self.get_output_directory).pack(padx=5, pady=5, side='left')
        ttk.Label(t3_frm2, text='Número de reintentos:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
        self.retry_count_box = ttk.Combobox(t3_frm2, state='readonly', width=5, values=range(10),
                                            textvariable=self.retry_count)
        self.retry_count_box.set(3)
        self.retry_count_box.pack(padx=5, pady=5, side='left')
        ttk.Label(t3_frm3, text='Parche a la duracíon de la Demo:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')                                                                                     
        self.patch_demo_true = ttk.Radiobutton(t3_frm3, text='Si', variable=self.patch_demo, value=True)
        self.patch_demo_false = ttk.Radiobutton(t3_frm3, text='No', variable=self.patch_demo, value=False)
        self.patch_demo_true.pack(padx=5, pady=5, side='left')
        self.patch_demo_false.pack(padx=5, pady=5, side='left')
        ttk.Label(t3_frm4, text='Parche al DLC:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
        self.patch_dlc_true = ttk.Radiobutton(t3_frm4, text='Si', variable=self.patch_dlc, value=True)
        self.patch_dlc_false = ttk.Radiobutton(t3_frm4, text='No', variable=self.patch_dlc, value=False)
        self.patch_dlc_true.pack(padx=5, pady=5, side='left')
        self.patch_dlc_false.pack(padx=5, pady=5, side='left')
        ttk.Label(t3_frm5, text='Modo solo Tickets:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
        self.tickets_only_true = ttk.Radiobutton(t3_frm5, text='Si', variable=self.tickets_only, value=True)
        self.tickets_only_false = ttk.Radiobutton(t3_frm5, text='No', variable=self.tickets_only, value=False)
        self.tickets_only_true.pack(padx=5, pady=5, side='left')
        self.tickets_only_false.pack(padx=5, pady=5, side='left')
        ttk.Label(t3_frm6, text='Modo de simulación:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
        self.simulate_mode_true = ttk.Radiobutton(t3_frm6, text='Si', variable=self.simulate_mode, value=True)
        self.simulate_mode_false = ttk.Radiobutton(t3_frm6, text='No', variable=self.simulate_mode, value=False)
        self.simulate_mode_true.pack(padx=5, pady=5, side='left')
        self.simulate_mode_false.pack(padx=5, pady=5, side='left')
        ttk.Label(t3_frm7, text='Elija su comportamiento de descarga preferido:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
        
        ttk.Radiobutton(t3_frm8, text=('Descargar tickets legítimos para títulos cuando estén disponibles y generar tickets falsos para '
                        'títulos que no tengan un ticket legítimo.'), variable=self.dl_behavior, value=1, command=self.toggle_widgets).pack(padx=5, pady=5,
                                                                                                                         side='left')                                                                                                                                                           
        ttk.Radiobutton(t3_frm9, text='Sólo descarga títulos con tickets legítimos e ignora todos los demás.',
                        variable=self.dl_behavior, value=2, command=self.toggle_widgets).pack(padx=5, pady=5, side='left')
        
        ttk.Checkbutton(self.t3_frm10, text='Quitar elementos omitidos de la lista de descargas cuando se realiza.',
                        variable=self.remove_ignored).pack(padx=5, pady=5, side='left')
        
        ttk.Label(t3_frm11, text='Auto-detectar game, updates y dlc:', font='Helvetica 10 bold').pack(padx=15, pady=5, side='left')
                                                                                                                                                                                                           
        ttk.Label(t3_frm12, text=('Cuando se agreguen juegos a la lista de descarga, automaticamente puedes añadir '
                                  'updates y dlc.')).pack(padx=5, side='left')
        
        ttk.Radiobutton(t3_frm13, text='Desactivado', variable=self.auto_fetching, value='disabled',
                        command=self.toggle_widgets).pack(padx=5, pady=5, side='left')
        
        ttk.Radiobutton(t3_frm14, text='Sugerir contenido a añadir', variable=self.auto_fetching,
                        value='prompt', command=self.toggle_widgets).pack(padx=5, pady=5, side='left')
        
        ttk.Radiobutton(t3_frm15, text='Automaticamente añadir contenido:', variable=self.auto_fetching, value='auto',
                        command=self.toggle_widgets).pack(padx=5, pady=5, side='left')
        
        ttk.Checkbutton(self.t3_frm16, text='Buscar update del juego', variable=self.fetch_updates).pack(padx=15, pady=5, side='left')
        
        ttk.Checkbutton(self.t3_frm16, text='Buscar dlc del juego', variable=self.fetch_dlc).pack(padx=5, pady=5, side='left')
        
        ttk.Checkbutton(self.t3_frm16, text='Permitir auto-busqueda cuando\nse hagan importaciones',
                        variable=self.fetch_on_batch).pack(padx=5, pady=5, side='left')
        
        ttk.Label(t3_frm17, text='Número de subprocesos que se usarán al descargar:', font='Helvetica 10 bold').pack(side='left', padx=15)
        
        self.throttler = tk.Scale(t3_frm17, from_=1, to=5, length=200, tickinterval=1, orient='horizontal',
                                  variable=self.total_thread_count)
        self.throttler.pack(side='left')
        
        ttk.Button(t3_frm18, text='Guardar ajustes', width=20, command=self.save_settings).pack(padx=10, pady=10, anchor='n')                                                                                                                                                                                                           
        ttk.Button(t3_frm18, text='Restablecer ajustes', width=20, command=lambda: self.load_settings(reset=True)).pack(padx=10, pady=10,
                                                                                                                   anchor='s')
        t3_frm1.grid(row=1, column=1, sticky='w')
        t3_frm2.grid(row=2, column=1, sticky='w')
        t3_frm3.grid(row=3, column=1, sticky='w')
        t3_frm4.grid(row=4, column=1, sticky='w')
        t3_frm5.grid(row=5, column=1, sticky='w')
        t3_frm6.grid(row=6, column=1, sticky='w')
        t3_frm7.grid(row=7, column=1, sticky='w')
        t3_frm8.grid(row=8, column=1, padx=40, sticky='w')
        t3_frm9.grid(row=9, column=1, padx=40, sticky='w')
        self.t3_frm10.grid(row=10, column=1, padx=80, sticky='w')
        t3_frm11.grid(row=11, column=1, sticky='w')
        t3_frm12.grid(row=12, column=1, padx=40, sticky='w')
        t3_frm13.grid(row=13, column=1, padx=40, sticky='w')
        t3_frm14.grid(row=14, column=1, padx=40, sticky='w')
        t3_frm15.grid(row=15, column=1, padx=40, sticky='w')
        self.t3_frm16.grid(row=16, column=1, padx=80, sticky='w')
        t3_frm17.grid(row=17, column=1, sticky='w')
        t3_frm18.grid(row=18, column=1, padx=10, pady=20, sticky='w')

        # Tab 4
        t4_frm0 = ttk.Frame(tab4)
        t4_frm1 = ttk.Frame(tab4)
        t4_frm2 = ttk.Frame(tab4)
        t4_frm3 = ttk.Frame(tab4)
        t4_frm4 = ttk.Frame(tab4)
        t4_frm5 = ttk.Frame(tab4)
        t4_frm6 = ttk.Frame(tab4)
        t4_frm7 = ttk.Frame(tab4)
        t4_frm8 = ttk.Frame(tab4)
        t4_frm9 = ttk.Frame(tab4)
        t4_frm10 = ttk.Frame(tab4)
        t4_frm11 = ttk.Frame(tab4)

        ttk.Label(t4_frm0, text='Información de la versión:\n').pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm1, text='Aplicación GUI:', font="Helvetica 13 bold").pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm2, text='Versión actual:\nPara la aplicacíon:').pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm2, text=__VERSION__ + '\n' + targetversion).pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm3, text='Última versión disponible:').pack(padx=5, pady=5, side='left')
        ttk.Label(t4_frm3, textvariable=self.newest_gui_ver).pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm4, text='Actualizar a la última versión:').pack(padx=5, pady=1, side='left')
        ttk.Button(t4_frm4, text='Actualizar', command=lambda: self.update_application('gui', self.versions['gui_new'])).pack(padx=5, pady=1,
                                                                                                                          side='left')
                                                                                                                             
        ttk.Label(t4_frm7, text='Aplicación ALUCARDIANOS WUP HELPER:', font="Helvetica 13 bold").pack(padx=5, pady=5, side='left')                                                                                  
        ttk.Label(t4_frm8, text='Versión actual:').pack(padx=5, pady=1, side='left')
        ttk.Label(t4_frm8, text=fnku.__VERSION__).pack(padx=5, pady=1, side='left')

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

        # Tab 5
        t5_frm1 = ttk.Frame(self.tab5)
        t5_frm2 = ttk.Frame(self.tab5)
        t5_frm3 = ttk.Frame(self.tab5)
        t5_frm4 = ttk.Frame(self.tab5)
        t5_frm5 = ttk.Frame(self.tab5)
        t5_frm6 = ttk.Frame(self.tab5)
        t5_frm7 = ttk.Frame(self.tab5)
        t5_frm8 = ttk.Frame(self.tab5)
        t5_frm9 = ttk.Frame(self.tab5)
        t5_frm10 = ttk.Frame(self.tab5)
        t5_frm11 = ttk.Frame(self.tab5)

        ttk.Label(t5_frm1, text='Progreso total de la descarga:', font='Helvetica 10 bold').pack(side='left')
        self.progressbar = ttk.Progressbar(t5_frm1, orient='horizontal', length=325, mode='determinate')
        self.progressbar.pack(padx=10, side='left')
        ttk.Label(t5_frm1, textvariable=self.dl_percentage_string).pack(side='left', padx=10)
        ttk.Label(t5_frm1, textvariable=self.dl_progress_string).pack(side='left')
        ttk.Label(t5_frm1, text='/').pack(side='left')
        ttk.Label(t5_frm1, textvariable=self.dl_total_string).pack(side='left')
        ttk.Label(t5_frm3, text='Estado:', font='Helvetica 10 bold').pack(side='left')
        ttk.Label(t5_frm4, textvariable=self.thread1_status).pack(padx=10, side='left')
        ttk.Label(t5_frm5, textvariable=self.thread2_status).pack(padx=10, side='left')
        ttk.Label(t5_frm6, textvariable=self.thread3_status).pack(padx=10, side='left')
        ttk.Label(t5_frm7, textvariable=self.thread4_status).pack(padx=10, side='left')
        ttk.Label(t5_frm8, textvariable=self.thread5_status).pack(padx=10, side='left')
        ttk.Label(t5_frm9, text='DESCARGAS FALLIDAS:', font='Helvetica 10 bold').pack(side='bottom')
        failed_scroller = ttk.Scrollbar(t5_frm10, orient='vertical')
        failed_scroller.pack(side='right', fill='y')
        self.failed_box = tk.Text(t5_frm10, width=20, height=8, state='disabled')
        self.failed_box.pack(side='right', fill='both', expand=True)
        self.failed_box.config(yscrollcommand=failed_scroller.set)
        failed_scroller.config(command=self.failed_box.yview)
        log_scroller = ttk.Scrollbar(t5_frm11, orient='vertical')
        log_scroller.pack(side='right', fill='y')
        self.log_box = tk.Text(t5_frm11, state='disabled')
        self.log_box.pack(side='right', fill='both', expand=True)
        self.log_box.config(yscrollcommand=log_scroller.set)
        log_scroller.config(command=self.log_box.yview)
        ttk.Label(t5_frm11, text='Log:', font='Helvetica 10 bold').pack(side='top', padx=15)

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

        self.load_program_revisions()
        self.load_settings()
        self.toggle_widgets()
        self.load_title_sizes()
        self.build_database()

        if os.path.isfile('config.json'):
            self.populate_selection_list()

        ## Build an sqlite database of all the data in the titlekeys json as well as size information
        ## for the title. Raw size in bytes as well as human readable size is recorded.
        ## The database that ships with the releases are minimal, containing ONLY size information.
        ## A full db build is mostly for redundancy and can be built by deleting the old data.db file,
        ## uncomment self.build_database(sizeonly=False) below and run the program.
        ## Be sure to re-comment out self.build_database(sizeonly=False) before running the program again.
        ## This will take a short while to fetch all the download size information.

        # self.build_database(sizeonly=False)

    def build_database(self, sizeonly=True):
        if len(self.title_sizes) >= len(self.title_data):
            return
        
        print('\nActualizando información de la base de datos.....\n')
        dataset = []
        compare_ids = []
        TK = fnku.TK
        
        try:
            update_count = len(self.title_data) - len(self.title_sizes)
        except:
            update_count = len(self.title_data)
            
        message.showinfo('Update database', ('Your size info database needs to be updated. We will update {} entries now and '
                                             'continue when it\'s done').format(update_count), parent=self)
        
        if not os.path.isfile('data.db'):
            db = sqlite3.connect('data.db')
            cursor = db.cursor()
            cursor.execute(("CREATE TABLE titles(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                            "title_id TEXT, title_key TEXT, name TEXT, region TEXT, content_type TEXT, "
                            "size TEXT, ticket INT, raw_size INT)"))
        else:
            db = sqlite3.connect('data.db')
            cursor = db.cursor()
        cursor.execute("SELECT title_id FROM titles")

        for i in cursor:
            compare_ids.append(str(i[0]))

        loopcounter = 1
        for i in self.title_data:
            if not str(i[2]) in compare_ids:
                print('Obteniendo información de la base de datos, título {} de {}'.format(loopcounter, update_count))
                name = i[0]
                region = i[1]
                tid = i[2]
                tkey = i[3]
                cont = i[4]
                if tid in self.has_ticket:
                    tick = 1
                else:
                    tick = 0

                sz = 0
                total_size = 0
                baseurl = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/{}'.format(tid)

                if not fnku.download_file(baseurl + '/tmd', 'title.tmd', 1):
                    print('ERROR: no se pudo descargar TMD...')
                else:
                    with open('title.tmd', 'rb') as f:
                        tmd = f.read()
                        
                    content_count = int(binascii.hexlify(tmd[TK + 0x9E:TK + 0xA0]), 16)
                    total_size = 0
                    for i in range(content_count):
                        c_offs = 0xB04 + (0x30 * i)
                        c_id = binascii.hexlify(tmd[c_offs:c_offs + 0x04]).decode()
                        total_size += int(binascii.hexlify(tmd[c_offs + 0x08:c_offs + 0x10]), 16)
                        
                    sz = fnku.bytes2human(total_size)
                    os.remove('title.tmd')

                dataset.append((tid, tkey, name, region, cont, sz, total_size, tick))
                loopcounter += 1

        if len(dataset) > 0:
            for i in dataset:
                tid = i[0]
                tkey = i[1]
                name = i[2]
                region = i[3]
                cont = i[4]
                sz = i[5]
                raw = i[6]
                tick = i[7]
                if sizeonly:
                    cursor.execute("""INSERT INTO titles (title_id, size, raw_size) VALUES (?, ?, ?)""", (tid, sz, raw))
                else:
                    cursor.execute(("INSERT INTO titles (title_id, title_key, name, region, content_type, size, ticket, "
                                    "raw_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"), (tid, tkey, name, region, cont, sz, tick, raw))
                        
        db.commit()
        db.close()
        print('hecho escribiendo en la base de datos.')
        message.showinfo('Done', 'Done updatating database', parent=self)
        

    def load_title_sizes(self):
        if os.path.isfile('data.db'):
            db = sqlite3.connect('data.db')
            cursor = db.cursor()
            cursor.execute("""SELECT title_id, size, raw_size FROM titles""")
            for i in cursor:
                self.title_sizes[str(i[0])] = str(i[1])
                self.title_sizes_raw[str(i[0])] = str(i[2])
            db.close()
        else:
            print('No se encontró el archivo data.db.')
            self.title_sizes = {}
            self.title_sizes_raw = {}
            

    def id_changed(self, *args):
        self.key_box.delete('0', tk.END)
        t_id = self.id_box.get()
        if len(t_id) == 16:
            try:
                if t_id in self.has_ticket:
                    self.has_ticket_lbl.configure(text='SI', foreground='green')
                else:
                    self.has_ticket_lbl.configure(text='NO', foreground='red')
                if self.title_dict[t_id].get('key', None):
                    self.key_box.insert('end', self.title_dict[t_id]['key'])
                if self.title_sizes.get(t_id, None):
                    self.dl_size_lbl.configure(text='Size: ' + self.title_sizes[t_id] + ',')
                else:
                    self.dl_size_lbl.configure(text='Size: ?,')

            except Exception as e:
                print(e)
                self.dl_size_lbl.configure(text='Size: ?,')

        else:
            if self.dl_size_lbl.cget('text') != 'Size:,':
                self.dl_size_lbl.configure(text='Size:,')
            if self.has_ticket_lbl.cget('text') != '':
                self.has_ticket_lbl.configure(text='')
                

    def update_keysite_widgets(self):
        txt = 'Tickets cargados correctamente'
        self.enterkeysite_lbl.configure(text=txt, background='black', foreground='green', font="Helvetica 13 bold")
        self.http_lbl.pack_forget()
        self.keysite_box.pack_forget()
        self.submitkeysite_btn.pack_forget()
        

    def check_config_keysite(self):
        keysite = fnku.get_keysite()
        print(u'Descargar/actualizar datos de {}'.format(keysite))
        try:
            if not fnku.download_file('{}/json'.format(keysite), 'titlekeys.json', 3):
                message.showerror('Error', ('Could not download data file. Either the site is down\nor '
                                  'the saved keysite is incorrect. You can enter a new\nkeysite and try again.'))
            else:
                return True

        except ValueError:
            message.showerror('Error', ('The saved keysite does not appear to be a valid url.\nPlease '
                              'enter a new keysite url. Remember, you MUST include\nthe http:// or https://'))
        except IOError:
            pass
        

    def notify_of_update(self, update=True):
        txt = 'Hay una actualización disponible en el apartado de actualizaciones'
        fg = 'red'
        if not update:
            txt = 'No hay actualizaciones disponibles'
            fg = 'green'
        self.updatelabel.configure(text=txt, background='black', foreground=fg, font="Helvetica 13 bold")


    def update_application(self, app, zip_file):
        if app == 'fnku':
            self.download_zip(self.versions['fnku_url'].split('releases')[0] + 'archive' + '/v' + zip_file + '.zip')
        else:
            self.download_zip(self.versions['gui_url'].split('releases')[0] + 'archive' + '/v' + zip_file + '.zip')

        if self.unpack_zip('update.zip'):
            print('Actualización completada con éxito! Reinicie la aplicación\para que los cambios surtan efecto.')
            os.remove('update.zip')


    def unpack_zip(self, zip_name):
        try:
            print('descomprimir la actualización')
            cwd = os.getcwd()
            dest = os.path.join(os.getcwd(),zip_name)
            zfile = zipfile.ZipFile(dest, 'r')
            for i in zfile.namelist():
                if i[-3:] in ('.py', 'ppm', '.db', 'son'):
                    data = zfile.read(i, None)
                    x = i.split("/")[1]
                    if x != '':
                        with open(x, 'wb') as p_file:
                            p_file.write(data)
            zfile.close()
            return True
            
        except Exception as e:
            print('Error:', e)
            return False


    def download_zip(self, url):
        try:
            z = urlopen(url)
            print('Descargando ', url)
            with open('update.zip', "wb") as f:
                f.write(z.read())

        except HTTPError as e:
            print("Error:", e.code, url)
        except URLError as e:
            print ("Error:", e.reason, url)


    def populate_selection_list(self, download_data=True):
        if download_data:
            if self.check_config_keysite():
                self.update_keysite_widgets()
                self.nb.select(self.tab2)
        try:
            self.clear_id_key_boxes()
            self.selection_list = []
            self.load_title_data()

            if self.filter_usa.get():
                if self.filter_game.get():
                    for i in self.usa_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.usa_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_update.get():
                    for i in self.usa_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_demo.get():
                    for i in self.usa_selections['demo']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_system.get():
                    for i in self.usa_selections['system']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)

            if self.filter_eur.get():
                if self.filter_game.get():
                    for i in self.eur_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.eur_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_update.get():
                    for i in self.eur_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_demo.get():
                    for i in self.eur_selections['demo']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_system.get():
                    for i in self.eur_selections['system']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)

            if self.filter_jpn.get():
                if self.filter_game.get():
                    for i in self.jpn_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.jpn_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_update.get():
                    for i in self.jpn_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_demo.get():
                    for i in self.jpn_selections['demo']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_system.get():
                    for i in self.jpn_selections['system']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)

            self.selection_list.sort()
            self.user_search_var.set('')
            self.update_selection_box()

            print('Se llenó con éxito la lista de selección..')
        except Exception as e:
            print('Algo sucedió al intentar completar la lista de selección...')
            print('ERROR:', e)


    def update_selection_box(self, *args):
        if len(args) == 0:
            sel_list = self.selection_list
        else:
            sel_list = args[0]
        self.selection_box.delete('0', tk.END)

        for i in sel_list:
            self.selection_box.insert('end', i)


    def clear_id_key_boxes(self, *args):
        self.id_box.delete('0', tk.END)
        self.key_box.delete('0', tk.END)


    def selection_box_changed(self, event):
        widget = event.widget
        sel = widget.curselection()
        user_selected_raw = widget.get(sel)
        self.clear_id_key_boxes()
        titleid = self.reverse_title_names[user_selected_raw]
        self.id_box.insert('end', titleid)


    def user_search_changed(self, *args):
        search = self.user_search_var.get().lower()
        matches = []
        for i in self.selection_list:
            if search in i.lower():
                matches.append(i)
                matches.sort()
        self.update_selection_box(matches)


    def toggle_widgets(self):
        if self.show_batch.get():
            for i in self.batch_frames:
                i.grid()
        else:
            for i in self.batch_frames:
                i.grid_remove()

        if self.dl_behavior.get() == 2:
            self.t3_frm10.grid()
        else:
            self.t3_frm10.grid_remove()

        if self.auto_fetching.get() == 'auto':
            self.t3_frm16.grid()
        else:
            self.t3_frm16.grid_remove()


    def export_to_batch(self):
        outf = filedialog.asksaveasfilename(defaultextension='.txt')
        if outf:
            with open(outf, 'w') as f:
                for i in self.download_list:
                    f.write(i[1].strip() + '\n')
            message.showinfo('Complete', 'Done exporting batch job to file')


    def batch_import(self):
        titles = []
        inf = filedialog.askopenfilename()
        if inf:
            with open(inf, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip().strip('\n')
                    line = line.replace('-', '')
                    if len(line) == 16:
                        titles.append(line)
            if len(titles) > 0:
                self.add_to_list(titles, batch=True)

    # Parse the titlekeys.json file into categories and load them into dictionaries used by the program
    def load_title_data(self):
        self.title_data = []
        try:
            if not os.path.isfile('titlekeys.json'):
                return
            with open('titlekeys.json') as td:
                title_data = json.load(td)
            self.errors = 0
            print('Ahora analizando titlekeys.json')
            for i in title_data:
                try:
                    if i['name']:
                        titleid = i['titleID']
                        if self.title_sizes_raw.get(titleid, '0') == '0':  # Filter titles not available for download
                            continue
                        name = i['name']
                        name = name.lower().capitalize().strip()
                        titlekey = i['titleKey']
                        region = i['region']
                        tick = i['ticket']
                        if titleid[4:8] == '0010' or titleid[4:8] == '0030':
                            content_type = 'SYSTEM'
                        elif titleid[4:8] == '0000':
                            content_type = 'GAME'
                        elif titleid[4:8] == '000c':
                            content_type = 'DLC'
                        elif titleid[4:8] == '000e':
                            content_type = 'UPDATE'
                        elif titleid[4:8] == '0002':
                            content_type = 'DEMO'

                        if tick == '1':
                            self.has_ticket.append(titleid)

                        longname = name + '  --' + region + '  -' + content_type
                        entry = (name, region, titleid, titlekey, content_type, longname)
                        entry2 = (longname)
                        self.reverse_title_names[longname] = titleid
                        self.title_dict[titleid] = {'name': name, 'region': region, 'key': titlekey,
                                                    'type': content_type, 'longname': longname, 'ticket': tick}

                        if not entry in self.title_data:
                            self.title_data.append(entry)
                            if region == 'USA':
                                if content_type == 'GAME':
                                    if not entry2 in self.usa_selections['game']:
                                        self.usa_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.usa_selections['dlc']:
                                        self.usa_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.usa_selections['update']:
                                        self.usa_selections['update'].append(entry2)
                                elif content_type == 'DEMO':
                                    if not entry2 in self.usa_selections['demo']:
                                        self.usa_selections['demo'].append(entry2)
                                elif content_type == 'SYSTEM':
                                    if not entry2 in self.usa_selections['system']:
                                        self.usa_selections['system'].append(entry2)
                            elif region == 'EUR':
                                if content_type == 'GAME':
                                    if not entry2 in self.eur_selections['game']:
                                        self.eur_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.eur_selections['dlc']:
                                        self.eur_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.eur_selections['update']:
                                        self.eur_selections['update'].append(entry2)
                                elif content_type == 'DEMO':
                                    if not entry2 in self.eur_selections['demo']:
                                        self.eur_selections['demo'].append(entry2)
                                elif content_type == 'SYSTEM':
                                    if not entry2 in self.eur_selections['system']:
                                        self.eur_selections['system'].append(entry2)
                            elif region == 'JPN':
                                if content_type == 'GAME':
                                    if not entry2 in self.jpn_selections['game']:
                                        self.jpn_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.jpn_selections['dlc']:
                                        self.jpn_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.jpn_selections['update']:
                                        self.jpn_selections['update'].append(entry2)
                                elif content_type == 'DEMO':
                                    if not entry2 in self.jpn_selections['demo']:
                                        self.jpn_selections['demo'].append(entry2)
                                elif content_type == 'SYSTEM':
                                    if not entry2 in self.jpn_selections['system']:
                                        self.jpn_selections['system'].append(entry2)
                except Exception as e:
                    if DEBUG:
                        print('Error on title: ' + titleid)
                        print('ERROR DE CARGA ', e)
                        self.errors += 1
        except IOError:
            print('No se encontró ningún archivo titlekeys.json. El cuadro de selección estará vacío')
        if DEBUG: print(str(self.errors) + ' Titles did not load correctly.')


    def sanity_check_input(self, val, chktype):
        try:
            if chktype == 'title':
                if len(val) == 16:
                    val = int(val, 16)
                    return True
            elif chktype == 'key':
                if len(val) == 32:
                    val = int(val, 16)
                    return True
            else:
                return False
        except ValueError:
            return False


    def fetch_related_content(self, tid):
        if not self.fetch_dlc.get and not self.fetch_updates.get():
            return
        update = None
        dlc = None
        up_id = 'e'
        dlc_id = 'c'
        tryupid = tid[:7] + up_id + tid[8:]
        trydlcid = tid[:7] + dlc_id + tid[8:]
        if self.title_dict.get(tryupid, None):
            update = tryupid
        if self.title_dict.get(trydlcid, None):
            dlc = trydlcid
        titles = {'update': update, 'dlc': dlc}
        return titles


    def save_settings(self):
        x = (self.output_dir.get(), self.retry_count.get(), self.patch_demo.get(), self.patch_dlc.get(),
             self.tickets_only.get(), self.simulate_mode.get(), self.fetch_dlc.get(), self.fetch_updates.get(),
             self.remove_ignored.get(), self.auto_fetching.get(), self.fetch_on_batch.get(), self.dl_behavior.get(),
             self.total_thread_count.get(), self.filter_usa.get(), self.filter_eur.get(), self.filter_jpn.get(),
             self.filter_dlc.get(), self.filter_game.get(), self.filter_update.get(), self.filter_demo.get(),
             self.filter_system.get(), self.filter_hasticket.get())
        
        settings = {'output_dir': x[0], 'retry_count': x[1], 'patch_demo': x[2], 'patch_dlc': x[3],
                    'tickets_only': x[4], 'simulate_mode': x[5], 'fetch_dlc': x[6], 'fetch_updates': x[7],
                    'remove_ignored': x[8], 'auto_fetching': x[9], 'fetch_on_batch': x[10], 'dl_behavior': x[11],
                    'throttle': x[12], 'filter_usa': x[13], 'filter_eur': x[14], 'filter_jpn': x[15],
                    'filter_dlc': x[16], 'filter_game': x[17], 'filter_update': x[18], 'filter_demo': x[19],
                    'filter_system': x[20], 'filter_hasticket': x[21]}
        
        with open('guisettings.json', 'w') as f:
            json.dump(settings, f)


    def load_settings(self, reset=False):
        if reset:
            self.output_dir.set('')
            self.retry_count.set(3)
            self.patch_demo.set(True)
            self.patch_dlc.set(True)
            self.tickets_only.set(False)
            self.simulate_mode.set(False)
            self.fetch_dlc.set(True)
            self.fetch_updates.set(True)
            self.remove_ignored.set(True)
            self.auto_fetching.set('prompt')
            self.fetch_on_batch.set(False)
            self.dl_behavior.set(1)
            self.save_settings()
            self.throttler.set(5)
            self.filter_usa.set(True)
            self.filter_eur.set(True)
            self.filter_jpn.set(True)
            self.filter_dlc.set(True)
            self.filter_game.set(True)
            self.filter_update.set(True)
            self.filter_demo.set(True)
            self.filter_system.set(True)
            self.filter_hasticket.set(False)
            return

        with open('guisettings.json', 'r') as f:
            x = json.load(f)
            
        self.output_dir.set(x['output_dir'])
        self.retry_count.set(x['retry_count'])
        self.patch_demo.set(x['patch_demo'])
        self.patch_dlc.set(x['patch_dlc'])
        self.tickets_only.set(x['tickets_only'])
        self.simulate_mode.set(x['simulate_mode'])
        self.fetch_dlc.set(x['fetch_dlc'])
        self.fetch_updates.set(x['fetch_updates'])
        self.remove_ignored.set(x['remove_ignored'])
        self.auto_fetching.set(x['auto_fetching'])
        self.fetch_on_batch.set(x['fetch_on_batch'])
        self.dl_behavior.set(x['dl_behavior'])
        self.throttler.set(x['throttle'])
        self.filter_usa.set(x['filter_usa'])
        self.filter_eur.set(x['filter_eur'])
        self.filter_jpn.set(x['filter_jpn'])
        self.filter_dlc.set(x['filter_dlc'])
        self.filter_game.set(x['filter_game'])
        self.filter_update.set(x['filter_update'])
        self.filter_demo.set(x['filter_demo'])
        self.filter_system.set(x['filter_system'])
        self.filter_hasticket.set(x['filter_hasticket'])


    def add_to_list(self, titles, batch=False):
        do_add_update = False
        do_add_dlc = False
        fetch_bhvr = self.auto_fetching.get()
        fetch_on_batch = self.fetch_on_batch.get()
        fetch_updates = self.fetch_updates.get()
        fetch_dlc = self.fetch_dlc.get()
        if not batch:
            if not len(titles[0]) == 16:
                message.showerror('No title id', 'You did not provide a 16 digit title id')
                return
            if fetch_bhvr != 'disabled':
                if titles[0][7] == '0':
                    fetched = self.fetch_related_content(titles[0])
                    try:
                        if fetched:
                            if fetch_updates:
                                if fetched['update']:
                                    if fetch_bhvr == 'prompt':
                                        if message.askyesno('Game update is available', ('There is an update available for this game, '
                                                            'would you like to add it to\nthe list as well?')):
                                            titles.append(fetched['update'])

                                    elif fetch_bhvr == 'auto':
                                        titles.append(fetched['update'])
                            if fetch_dlc:
                                if fetched['dlc']:
                                    if fetch_bhvr == 'prompt':
                                        if message.askyesno('Game dlc is available', ('There is dlc available for this game, '
                                                            'would you like to add it to\nthe list as well?')):
                                            titles.append(fetched['dlc'])
                                    elif fetch_bhvr == 'auto':
                                        titles.append(fetched['dlc'])
                    except:
                        pass

        else:
            if fetch_bhvr == 'auto' and fetch_on_batch:
                for title in titles[:]:
                    if title[7] == '0':
                        fetched = self.fetch_related_content(title)
                    try:
                        if fetched:
                            if fetched['update'] and fetch_updates:
                                titles.append(fetched['update'])
                            if fetched['dlc'] and fetch_dlc:
                                titles.append(fetched['dlc'])
                    except Exception as e:
                        print(e)

        for titleid in titles:
            if len(titleid) == 16:
                td = self.title_dict.get(titleid, {})
                key = None
                name = td.get('longname', titleid)
                name = '  ' + name
                if self.sanity_check_input(titleid, 'title'):
                    pass
                else:
                    print('Bad Title ID. Debe ser un hexadecimal de 16 dígitos.')
                    print('Title: ' + titleid)
                    continue

                key = td.get('key', self.key_box.get().strip())
                if key == '':
                    key = None
                if not key or self.sanity_check_input(key, 'key'):
                    pass
                else:
                    print('Bad Key. Must be a 32 digit hexadecimal.')
                    print('Title: ' + titleid)
                    continue

                size = int(self.title_sizes_raw.get(titleid, 0))
                if size == 0:
                    name = ' !' + name
                entry = (name, titleid, key, size)
                if not entry in self.download_list:
                    self.download_list.append(entry)

        self.populate_dl_listbox()


    def add_filtered_to_list(self):
        bulk = []
        for i in self.selection_list:
            if self.reverse_title_names.get(i, None):
                bulk.append(self.reverse_title_names[i])
        self.add_to_list(bulk, batch=True)


    def remove_from_list(self):
        try:
            index = self.dl_listbox.curselection()
            item = self.dl_listbox.get('anchor')
            for i in self.download_list:
                if i[0] == item:
                    self.download_list.remove(i)
            self.populate_dl_listbox()
        except IndexError as e:
            print('La lista de descargas ya está vacía')
            print(e)


    def clear_list(self):
        self.download_list = []
        self.populate_dl_listbox()


    def populate_dl_listbox(self):
        total_size = []
        trigger_warning = False
        self.dl_listbox.delete('0', tk.END)
        for i in self.download_list:
            name = i[0]
            if i[3] == 0:
                if not trigger_warning:
                    trigger_warning = True
            self.dl_listbox.insert('end', name)
            total_size.append(int(i[3]))
        total_size = sum(total_size)
        total_size = fnku.bytes2human(total_size)
        self.total_dl_size.set('Total size: ' + total_size)
        if trigger_warning:
            self.total_dl_size_warning.set(self.dl_warning_msg)
        else:
            self.total_dl_size_warning.set('')
        return


    def submit_key_site(self):
        site = self.keysite_box.get().strip()
        config = fnku.load_config()
        config['keysite'] = site
        fnku.save_config(config)
        print('Listo Guardado.')
        self.populate_selection_list()
        self.build_database()
        self.load_title_sizes()


    def get_output_directory(self):
        out_dir = filedialog.askdirectory()
        self.out_dir_box.delete('0', tk.END)
        self.out_dir_box.insert('end', out_dir)


    def load_program_revisions(self):
        print('Comprobando las actualizaciones del programa, esto podría tomar unos segundos.......\n')
        url = self.versions['gui_url']
        
        try:
            response = urlopen(url)
            rslts = response.read()
            rslts = str(rslts)
            x = ''
            for i in rslts:
                x = x + i
            parser = VersionParser()
            parser.feed(x)
            gui_data_set = parser.gui_data_set
            
        except Exception as e:
            print('NO PODRÍA CHEQUEAR LAS ACTUALIZACIONES')
            print('Verifique su conexión a Internet o actualice su Python a una versión >= 3.6.4')
            print('El siguiente error ocurrió:')
            gui_data_set = ['/dojafoja/null/null/v{}'.format(__VERSION__)]
            
        gui_all=[__VERSION__]
        gui_newest=''

        for i in gui_data_set:
            ver = LooseVersion(i.split('/')[4][1:-4])
            if ver > LooseVersion('2.0.5'):
                gui_all.append(ver)

        gui_newest = max(gui_all)
        if gui_newest > current_gui:
            self.notify_of_update()
        else:
            self.notify_of_update(update=False)

        self.versions['gui_all'] = [str(i) for i in gui_all]
        self.versions['gui_new'] = str(gui_newest)
        self.newest_gui_ver.set(gui_newest)


    def download_clicked(self):
        self.nb.select(self.tab5)
        self.thread1_status.set("")
        self.thread2_status.set("")
        self.thread3_status.set("")
        self.thread4_status.set("")
        self.thread5_status.set("")
        title_list = []
        key_list = []
        rtry_count = self.retry_count.get()
        ptch_demo = self.patch_demo.get()
        ptch_dlc = self.patch_dlc.get()
        tick_only = self.tickets_only.get()
        sim = self.simulate_mode.get()

        for i in self.download_list:
            title_list.append(i[1])
            key_list.append(i[2])

        ignored = []
        behavior = self.dl_behavior.get()

        joblist = []
        totalsize = 0
        RESULTQ.put(('log', '\n*** SESIÓN DE DESCARGADO COMENZADA:  {} ***'.format(self.get_timestamp())))
        for i in self.download_list[:]:
            out_dir = self.output_dir.get().strip()
            t = i[1]
            k = i[2]
            td = self.title_dict.get(t, {})
            n = td.get('name', '').strip()
            if td.get('type', '').strip() == 'DEMO':
                n = n + '_Demo'
            r = td.get('region', '').strip()

            if t in self.has_ticket or td.get('type', '') == 'UPDATE':
                rslt = fnku.process_title_id(t, None, name=n, region=r, output_dir=out_dir, retry_count=rtry_count,
                                             onlinetickets=True, patch_demo=ptch_demo, patch_dlc=ptch_demo,
                                             simulate=sim, tickets_only=tick_only, resultq=RESULTQ)

            else:
                if behavior == 2:
                    if self.remove_ignored.get():
                        self.download_list.remove(i)
                        self.populate_dl_listbox()
                        root.update()
                    ignored.append(i[1])
                    continue

                rslt = fnku.process_title_id(t, k, name=n, region=r, output_dir=out_dir, retry_count=rtry_count,
                                             patch_demo=ptch_demo,
                                             patch_dlc=ptch_demo, simulate=sim, tickets_only=tick_only, resultq=RESULTQ)
            if not rslt:
                if self.tickets_only.get():
                    return
                if self.simulate_mode.get():
                    return 
                RESULTQ.put(('fail','',t))
                return
            totalsize += rslt[1]
            self.download_list.remove(i)
            joblist.append(rslt[0])

        self.reset_progress()
        self.dl_total_float = totalsize
        self.dl_total_string.set(fnku.bytes2human(totalsize))
        self.progressbar['maximum'] = totalsize
        dlsession = DownloadSession(JOBQ, RESULTQ, self.total_thread_count.get())
        dlsession.populate_job(joblist)
        dlsession.poison_threads()
        self.active_thread_count = self.total_thread_count.get()
        self.download_button.configure(state='disabled')
        dlsession.start_session()
        self.populate_dl_listbox()
        self.update_idletasks()


    def update_progress(self, prog):
        self.dl_progress += prog
        self.dl_progress_string.set(fnku.bytes2human(self.dl_progress))
        self.progressbar['value'] = self.dl_progress
        try:
            percent = "{:.2%}".format(float(self.dl_progress) / self.dl_total_float)
        except ZeroDivisionError:
            percent = 0
        self.dl_percentage_string.set(percent)
        if self.active_thread_count == 0:
            self.progressbar['value'] = self.progressbar['maximum']
            self.dl_percentage_string.set('100%')
            self.download_button.configure(state='normal')
            self.update_thread_status('', finished=True)
            RESULTQ.put(('log', '*** SESIÓN DE DESCARGADO COMPLETADA:  {} ***'.format(self.get_timestamp())))
            self.active_thread_count = None # Prevent spamming gui after all threads are dead.
            

    def reset_progress(self):
        self.dl_progress = 0
        self.dl_progress_string.set('0')
        self.progressbar['maximum'] = 0
        self.progressbar['value'] = 0
        self.active_thread_count = 0


    def update_thread_status(self, status, finished=False):
        if finished:  
            self.thread1_status.set('La sesión de descargado ha completado.')
            self.thread2_status.set('')
            self.thread3_status.set('')
            self.thread4_status.set('')
            self.thread5_status.set('')
            return
        
        if status[1] == '1':
            self.thread1_status.set('Thread 1: {}'.format(status[2]))

        elif status[1] == '2':
            self.thread2_status.set('Thread 2: {}'.format(status[2]))

        elif status[1] == '3':
            self.thread3_status.set('Thread 3: {}'.format(status[2]))

        elif status[1] == '4':
            self.thread4_status.set('Thread 4: {}'.format(status[2]))

        elif status[1] == '5':
            self.thread5_status.set('Thread 5: {}'.format(status[2]))


    def get_timestamp(self):
        handle = datetime.now()
        ts = '{}/{}/{}  {}:{}.{}'.format(handle.year, handle.month, handle.day, handle.hour,
                                         handle.minute, handle.second)
        return ts


    def set_icon(self):
        icon = PhotoImage(file='icon.ppm')
        self.tk.call('wm', 'iconphoto', self._w, icon)


    def process_result_queue(self):
        progress = 0
        if not RESULTQ.empty():
            for i in range(RESULTQ.qsize()):
                results = RESULTQ.get()

                if results[0] == 'log':
                    self.log_box.configure(state='normal')
                    self.log_box.insert('end', results[1] + '\n')
                    self.log_box.configure(state='disabled')
                    self.log_box.see('end')

                elif results[0] == 'progress':
                    progress += results[1]

                elif results[0] == 'status':
                    self.update_thread_status(results)

                elif results[0] == 'thread died':
                    self.active_thread_count -= 1

                elif results[0] == 'fail':
                    if not results[2] in failed_downloads:
                        failed_downloads.append(results[2])
                        self.failed_box.configure(state='normal')
                        self.failed_box.insert('end', results[2] + '\n')
                        self.failed_box.configure(state='disabled')
            
            self.update_progress(progress)
            self.update_idletasks()

        self.after(500, self.process_result_queue) # Reschedule every .5 seconds




if __name__ == '__main__':
    root = RootWindow()
    root.title('ALUCARDIANOS WUP HELPER 1.0.4')
    root.minsize(800,600)
    root.geometry("990x{}".format(root.winfo_screenheight()))
    root.set_icon()
    root.after(1000, root.process_result_queue)
    root.mainloop()
    root.save_settings()
