#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

 This is a multi-language version of Funkii-UI. Spanish translations
 were provided by the Alucardianos team. 

 DO NOT MODIFY ANY STRINGS WRAPPED WITH lang[]
 lang is a dict containing the original phrase to be translated as the key
 and the translated phrase as the value.
 Instead, modify them in the translatons.py file for the appropriate language
 and ONLY modify the translated phrase value, not the original phrase key.


 If you would like to contribute to the multi-language feature of FunKii-UI,
 you are welcome to add a new languge entry in modules\language\translations.py and translate
 the phrases. You may need to adjust where the newline character is, a.k.a '\n'
 if your translation is much longer than the original, in order
 for it to display correctly and not push other widgets around on the grid.
 Send me a pull request on Github with your modified translations.py and I will
 update the gui options to include the new language.

 YOU ARE FREE TO MODIFY AND DISTRIBUTE ALL PORTIONS OF THIS SOFTWARE UNDER THE FOLLOWING TERMS:

   1. YOU MUST INCLUDE CREDITS TO ORIGINAL DEVELOPERS SOMEWHERE INSIDE THE PROGRAM AND SOURCE.
   2. YOU MUST NOT CLAIM ANY PORTIONS OF THE SOFTWARE, OTHER THAN YOUR MODIFICATONS, AS YOUR ORIGINAL WORK.
   3. YOU MUST MAKE IT CLEAR IN THE SOURCE WHERE YOU HAVE MODIFIED.
   4. YOU MUST NOT BE AN ASS.
   5. YOU TECHNICALLY DON'T NEED TO FOLLOW ANY OF THESE RULES, EXCEPT FOR RULE #4.
   6. IF YOU CHOOSE NOT TO FOLLOW THESE TERMS THEN YOU ARE IN CLEAR VIOLATION OF RULE #4.
   
 '''

try:  # Python 2 imports
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as message
    from Tkinter import Image
    from urllib2 import urlopen, URLError, HTTPError
    from Queue import Queue

except ImportError:  # Python 3 imports
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox as message
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
from datetime import datetime

#Custom imports
from modules.language import translations
from modules.frames import themebuilder
from modules.frames import welcome_tab
from modules.frames import download_tab
from modules.frames import options_tab
from modules.frames import updates_tab
from modules.frames import progress_tab
from modules.custom.version_parser import VersionParser
from modules.custom.threaded_downloader import DownloadSession
from modules.custom import ACOWD_mod as fnku

__VERSION__ = "3.0.0"

current_gui = LooseVersion(__VERSION__)
PhotoImage = tk.PhotoImage

JOBQ = Queue()
RESULTQ = Queue()
ABORTQ = Queue()

try:
    fnku_VERSION_ = str(fnku.__VERSION__)
    current_fnku = LooseVersion(fnku_VERSION_)
except:
    fnku__VERSION__ = "?"
    current_fnku = LooseVersion('0')



class RootWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)
        
        self.versions = {'gui_new': '', 'gui_all': '', 'gui_url': 'https://github.com/GeovanniMCh/ACO_WUP_DOWNLOADER/releases'}
        self.runningversion = __VERSION__
        self.targetversion = "ACOWD mod"
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
 
        self.load_gui_vars()
        
        self.welcometab = welcome_tab.WelcomeTab(master=self.nb, gui=self)
        self.downloadtab = download_tab.DownloadTab(master=self.nb, gui=self)
        self.downloadtab.rowconfigure(3, weight=2)
        self.downloadtab.columnconfigure(1, weight=2)
        self.downloadtab.columnconfigure(4, weight=2)
        self.optionstab = options_tab.OptionsTab(master=self.nb, gui=self)
        self.updatestab = updates_tab.UpdatesTab(master=self.nb, gui=self)
        self.progresstab = progress_tab.ProgressTab(master=self.nb, gui=self)
        self.progresstab.rowconfigure(22, weight=2)
        self.progresstab.columnconfigure(1, weight=2)
        self.progresstab.rowconfigure(7, weight=2)
        self.progresstab.columnconfigure(5, weight=2)
        
        self.nb.add(self.welcometab, text=lang["Welcome"])
        self.nb.add(self.downloadtab, text=lang["Download"])
        self.nb.add(self.optionstab, text=lang["Options"])
        self.nb.add(self.updatestab, text=lang["Updates"])
        self.nb.add(self.progresstab, text=lang["Progress"])
    
        
        # Create a custom element and layout for the ttk.Entry widget.
        # This is so ttk widget can be color-themed properly in Windows.
        self.custom_entry_style = ttk.Style()
        self.custom_entry_style.element_create("plain.field", "from", "classic")
        self.custom_entry_style.layout("EntryStyle.TEntry",
                            [('Entry.plain.field', {'children': [(
                                'Entry.background', {'children': [(
                                    'Entry.padding', {'children': [(
                                        'Entry.textarea', {'sticky': 'nswe'})],
                                            'sticky': 'nswe'})], 'sticky': 'nswe'})],
                                                'border':'1', 'sticky': 'nswe'})])
        self.load_settings()
        self.load_program_revisions()
        self.toggle_widgets()
        self.load_title_sizes()
        self.focus_force() # Was having weird issues with the Window mangager not giving focus sometimes
        
        if os.path.isfile(os.path.join('data','config.json')):
            if self.download_data_on_start.get():
                self.populate_selection_list()
            else:
                self.populate_selection_list(download_data=False)
                self.update_keysite_widgets()
        
        self.build_database()
                

        ## Build an sqlite database of all the data in the titlekeys json as well as size information
        ## for the title. Raw size in bytes as well as human readable size is recorded.
        ## The database that ships with the releases are minimal, containing ONLY size information.
        ## A full db build is mostly for redundancy and can be built by deleting the old data.db file,
        ## uncomment self.build_database(sizeonly=False) below and run the program.
        ## Be sure to re-comment out self.build_database(sizeonly=False) before running the program again.
        ## This will take a short while to fetch all the download size information.

        # self.build_database(sizeonly=False)

    def build_database(self, sizeonly=True):
        dataset = []
        missing_ids = []
        database_ids = []
        TK = fnku.TK

        if not os.path.isfile(os.path.join('data', 'data.db')):
            db = sqlite3.connect(os.path.join('data', 'data.db'))
            cursor = db.cursor()
            cursor.execute(("CREATE TABLE titles(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                            "title_id TEXT, title_key TEXT, name TEXT, region TEXT, content_type TEXT, "
                            "size TEXT, ticket INT, raw_size INT)"))
        else:
            db = sqlite3.connect(os.path.join('data', 'data.db'))
            cursor = db.cursor()
        cursor.execute("SELECT title_id FROM titles")

        for i in cursor:
            database_ids.append(str(i[0]))

        for i in self.title_data:
            if not i[2] in database_ids:
                missing_ids.append(i)

        update_count = len(missing_ids)
        if not update_count:
            return

        message.showinfo(lang['Update database'],
                         lang[("Your size info database needs to be updated. We will update {} entries now "
                               "and continue when it's done.")].format(update_count), parent=self)
        
        print('\n'+lang['Updating size information database now']+'.....\n')
        
        loopcounter = 1
        for i in missing_ids:
            print(lang['Fetching database info, title {} of {}'].format(loopcounter, update_count))
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
                print(lang['ERROR: Could not download TMD'])
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
                    cursor.execute(
                        ("INSERT INTO titles (title_id, title_key, name, region, content_type, size, ticket, "
                         "raw_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"), (tid, tkey, name, region, cont, sz, tick, raw))

        db.commit()
        db.close()
        self.load_title_sizes()
        self.populate_selection_list(download_data=False)
        message.showinfo(lang['Done'], lang['Done updatating database'], parent=self)
        

    def load_title_sizes(self):
        if os.path.isfile(os.path.join('data', 'data.db')):
            db = sqlite3.connect(os.path.join('data', 'data.db'))
            cursor = db.cursor()
            cursor.execute("""SELECT title_id, size, raw_size FROM titles""")
            for i in cursor:
                self.title_sizes[str(i[0])] = str(i[1])
                self.title_sizes_raw[str(i[0])] = str(i[2])
            db.close()
        else:
            print(lang['No data.db file found.'])
            self.title_sizes = {}
            self.title_sizes_raw = {}


    def id_changed(self, *args):
        self.key_box.delete('0', tk.END)
        t_id = self.id_box.get()
        if len(t_id) == 16:
            try:
                if t_id in self.has_ticket:
                    self.has_ticket_lbl.configure(text=lang['Yes'].upper())
                else:
                    self.has_ticket_lbl.configure(text=lang['No'].upper())
                if self.title_dict[t_id].get('key', None):
                    self.key_box.insert('end', self.title_dict[t_id]['key'])
                if self.title_sizes.get(t_id, None):
                    self.dl_size_lbl.configure(text=lang['Size:']+' ' + self.title_sizes[t_id] + ',')
                else:
                    self.dl_size_lbl.configure(text=lang['Size:']+' ?,')

            except Exception as e:
                print(e)
                self.dl_size_lbl.configure(text=lang['Size:']+' ?,')

        else:
            if self.dl_size_lbl.cget('text') != lang['Size:']+',':
                self.dl_size_lbl.configure(text=lang['Size:']+',')
            if self.has_ticket_lbl.cget('text') != '':
                self.has_ticket_lbl.configure(text='')


    def update_keysite_widgets(self):
        txt = lang['keysite is loaded']
        self.enterkeysite_lbl.configure(text=txt, font="Helvetica 13 bold")


    def check_config_keysite(self):
        keysite = fnku.get_keysite()
        print(lang['Downloading data from {}'].format(keysite))
        try:
            if not fnku.download_file('{}/json'.format(keysite), os.path.join('data', 'titlekeys.json'), 3):
                message.showerror(lang['Error'], lang[('Could not download data file. Either the site is down\nor the saved '
                                                       'keysite is incorrect. You can enter a new\nkeysite and try again.')])
            else:
                return True

        except ValueError:
            message.showerror(lang['Error'], lang[('The saved keysite does not appear to be a valid url.\nPlease '
                                                   'enter a new keysite url. Remember, you MUST include\nthe http:// or https://')])
        except IOError:
            pass


    def notify_of_update(self, update=True):
        if update:
            txt = lang['Updates are available in the updates tab']
            fg = 'red'
            message.showinfo(lang['Update available'], lang['An update is available for this program. Please see the updates tab to update.'])
        else:
            txt = lang['No updates are currently available']
            fg = None
        self.updatelabel.configure(text=txt, foreground=fg, font="Helvetica 13 bold")


    def update_application(self, app, zip_file):
        self.download_zip(self.versions['gui_url'].split('releases')[0] + 'archive' + '/v' + zip_file + '.zip')

        if self.unpack_zip('update.zip'):
            os.remove('update.zip')    
            message.showinfo(lang['Success'], lang['Restart application\nfor changes to take effect.'])
            

    def unpack_zip(self, zip_name):
        try:
            cwd = os.getcwd()
            dest = os.path.join(os.getcwd(), zip_name)
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
            print('Error'+':', e)
            return False


    def download_zip(self, url):
        try:
            z = urlopen(url)
            print(lang['Downloading']+' ', url)
            with open('update.zip', "wb") as f:
                f.write(z.read())

        except HTTPError as e:
            print(lang["Error"]+":", e.code, url)
        except URLError as e:
            print (lang["Error"]+":", e.reason, url)


    def populate_selection_list(self, download_data=True):
        if download_data:
            if self.check_config_keysite():
                self.update_keysite_widgets()
                #self.nb.select(self.self.downloadtab)
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

        except Exception as e:
            print(lang['Error']+':', e)


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
        try:
            widget = event.widget
            sel = widget.curselection()
            user_selected_raw = event.widget.get(sel)
            self.clear_id_key_boxes()
            titleid = self.reverse_title_names[user_selected_raw]
            self.id_box.insert('end', titleid)
        except:
            pass


    def user_search_changed(self, *args):
        search = self.user_search_var.get().lower()
        matches = []
        for i in self.selection_list:
            if search in i.lower():
                matches.append(i)
                matches.sort()
        self.update_selection_box(matches)


    def toggle_widgets(self):
        if self.auto_fetching.get() == 'auto':
            self.t3_frm16.grid()
        else:
            self.t3_frm16.grid_remove()


    # Parse the titlekeys.json file into categories and load them into dictionaries used by the program
    def load_title_data(self):
        self.raw_titlecount = 0
        self.title_data = []
        try:
            if not os.path.isfile(os.path.join('data', 'titlekeys.json')):
                return
            if sys.version_info[0] == 3:
                with open(os.path.join('data', 'titlekeys.json'), encoding='utf-8') as td:
                    title_data = json.load(td)
            else:
                with open(os.path.join('data', 'titlekeys.json')) as td:
                    title_data = json.load(td)
                    
            for i in title_data:
                if i['name']:
                    titleid = i['titleID']
                    
                    if self.title_sizes_raw.get(titleid, None) == '0':  # Filter titles not available for download
                        self.raw_titlecount += 1
                        continue
                    
                    name = i['name'].lower().capitalize().strip().replace('\n',' ')
                    titlekey = i.get('titleKey', '')
                    region = i['region']
                    tick = i['ticket']
                    if titleid[4:8] == '0010' or titleid[4:8] == '0030':
                        content_type = lang['System'].upper()
                    elif titleid[4:8] == '0000':
                        content_type = lang['Game'].upper()
                    elif titleid[4:8] == '000c':
                        content_type = 'DLC'
                    elif titleid[4:8] == '000e':
                        content_type = lang['Update'].upper()
                    elif titleid[4:8] == '0002':
                        content_type = lang['Demo'].upper()

                    if tick == '1' or tick == 1:
                        self.has_ticket.append(titleid)
                        
                    longname = u"{} --{} -{}".format(name, region, content_type)
                    entry = (name, region, titleid, titlekey, content_type, longname)
                    self.reverse_title_names[longname] = titleid
                    self.title_dict[titleid] = {'name': name, 'region': region, 'key': titlekey,
                                                'type': content_type, 'longname': longname, 'ticket': tick}

                    if not entry in self.title_data:
                        self.title_data.append(entry)
                        
                        if region == 'USA':
                            if content_type == lang['Game'].upper():
                                if not longname in self.usa_selections['game']:
                                    self.usa_selections['game'].append(longname)
                            elif content_type == 'DLC':
                                if not longname in self.usa_selections['dlc']:
                                    self.usa_selections['dlc'].append(longname)
                            elif content_type == lang['Update'].upper():
                                if not longname in self.usa_selections['update']:
                                    self.usa_selections['update'].append(longname)
                            elif content_type == lang['Demo'].upper():
                                if not longname in self.usa_selections['demo']:
                                    self.usa_selections['demo'].append(longname)
                            elif content_type == lang['System'].upper():
                                if not longname in self.usa_selections['system']:
                                    self.usa_selections['system'].append(longname)
                                    
                        elif region == 'EUR':
                            if content_type == lang['Game'].upper():
                                if not longname in self.eur_selections['game']:
                                    self.eur_selections['game'].append(longname)
                            elif content_type == 'DLC':
                                if not longname in self.eur_selections['dlc']:
                                    self.eur_selections['dlc'].append(longname)
                            elif content_type == lang['Update'].upper():
                                if not longname in self.eur_selections['update']:
                                    self.eur_selections['update'].append(longname)
                            elif content_type == lang['Demo'].upper():
                                if not longname in self.eur_selections['demo']:
                                    self.eur_selections['demo'].append(longname)
                            elif content_type == lang['System'].upper():
                                if not longname in self.eur_selections['system']:
                                    self.eur_selections['system'].append(longname)
                                    
                        elif region == 'JPN':
                            if content_type == lang['Game'].upper():
                                if not longname in self.jpn_selections['game']:
                                    self.jpn_selections['game'].append(longname)
                            elif content_type == 'DLC':
                                if not longname in self.jpn_selections['dlc']:
                                    self.jpn_selections['dlc'].append(longname)
                            elif content_type == lang['Update'].upper():
                                if not longname in self.jpn_selections['update']:
                                    self.jpn_selections['update'].append(longname)
                            elif content_type == lang['Demo'].upper():
                                if not longname in self.jpn_selections['demo']:
                                    self.jpn_selections['demo'].append(longname)
                            elif content_type == lang['System'].upper():
                                if not longname in self.jpn_selections['system']:
                                    self.jpn_selections['system'].append(longname)

                    self.raw_titlecount += 1
            
        except IOError as e:
            print(lang['Error']+':', e)

             
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
             self.auto_fetching.get(), self.fetch_on_batch.get(), self.dl_behavior.get(), self.total_thread_count.get(),
             self.filter_usa.get(), self.filter_eur.get(), self.filter_jpn.get(), self.filter_dlc.get(),
             self.filter_game.get(), self.filter_update.get(), self.filter_demo.get(), self.filter_system.get(),
             self.filter_hasticket.get(), self.download_data_on_start.get(), self.selected_theme.get())

        settings = {'output_dir': x[0], 'retry_count': x[1], 'patch_demo': x[2], 'patch_dlc': x[3],
                    'tickets_only': x[4], 'simulate_mode': x[5], 'fetch_dlc': x[6], 'fetch_updates': x[7],
                    'auto_fetching': x[8], 'fetch_on_batch': x[9], 'dl_behavior': x[10], 'throttle': x[11],
                    'filter_usa': x[12], 'filter_eur': x[13], 'filter_jpn': x[14], 'filter_dlc': x[15],
                    'filter_game': x[16], 'filter_update': x[17], 'filter_demo': x[18], 'filter_system': x[19],
                    'filter_hasticket': x[20], 'download_onstart': x[21], 'theme':x[22]}

        with open(os.path.join('data', 'guisettings.json'), 'w') as f:
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
            self.auto_fetching.set('prompt')
            self.fetch_on_batch.set(False)
            self.dl_behavior.set(1)
            self.save_settings()
            self.throttler.set(3)
            self.filter_usa.set(True)
            self.filter_eur.set(True)
            self.filter_jpn.set(True)
            self.filter_dlc.set(True)
            self.filter_game.set(True)
            self.filter_update.set(True)
            self.filter_demo.set(True)
            self.filter_system.set(True)
            self.filter_hasticket.set(False)
            self.download_data_on_start.set(True)
            self.selected_theme.set('Light')
            return

        with open(os.path.join('data', 'guisettings.json'), 'r') as f:
            x = json.load(f)

        self.output_dir.set(x['output_dir'])
        self.retry_count.set(x['retry_count'])
        self.patch_demo.set(x['patch_demo'])
        self.patch_dlc.set(x['patch_dlc'])
        self.tickets_only.set(x['tickets_only'])
        self.simulate_mode.set(x['simulate_mode'])
        self.fetch_dlc.set(x['fetch_dlc'])
        self.fetch_updates.set(x['fetch_updates'])
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
        self.download_data_on_start.set(x['download_onstart'])
        self.selected_theme.set(x['theme'])


    def add_to_list(self, titles, batch=False):
        print('titles', titles)
        fetch_bhvr = self.auto_fetching.get()
        fetch_on_batch = False
        fetch_updates = self.fetch_updates.get()
        fetch_dlc = self.fetch_dlc.get()
        if not batch:
            if not len(titles[0]) == 16:
                message.showerror(lang['Error'], lang['You did not provide a 16 digit title id'])
                return
            if fetch_bhvr != 'disabled':
                if titles[0][7] == '0':
                    fetched = self.fetch_related_content(titles[0])
                    try:
                        if fetched:
                            if fetch_updates:
                                if fetched['update']:
                                    if fetch_bhvr == 'prompt':
                                        if message.askyesno(lang['Game update is available'],
                                                            lang[('There is an update available for this game, '
                                                                  'would you like to add it to the list as well?')]):
                                            titles.append(fetched['update'])

                                    elif fetch_bhvr == 'auto':
                                        titles.append(fetched['update'])
                            if fetch_dlc:
                                if fetched['dlc']:
                                    if fetch_bhvr == 'prompt':
                                        if message.askyesno(lang['Game dlc is available'],
                                                            lang[('There is dlc available for this game, '
                                                                  'would you like to add it to the list as well?')]):
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
                name = td.get('longname', titleid)
                name = '  ' + name
                if self.sanity_check_input(titleid, 'title'):
                    pass
                else:
                    print(lang['Bad Title ID. Must be a 16 digit hexadecimal.'])
                    print('Title: ' + titleid)
                    continue

                key = td.get('key', self.key_box.get().strip())
                if key == '':
                    key = None
                if not key or self.sanity_check_input(key, 'key'):
                    pass
                else:
                    print(lang['Bad Key. Must be a 32 digit hexadecimal.'])
                    print('Title: ' + titleid)
                    continue

                size = int(self.title_sizes_raw.get(titleid, 0))
                if size == 0:
                    name = ' !' + name
                entry = (name, titleid, key, size)
                if not entry in self.download_list:
                    self.download_list.append(entry)
                    
        if not batch:
            self.populate_dl_listbox()



    def add_failed_to_download_list(self, titles):
        self.add_to_list(bulk, batch=True)


    def remove_from_list(self):
        try:
            index = self.dl_listbox.curselection()
            item = self.dl_listbox.get(index)
            for i in self.download_list:
                if i[0] == item:
                    self.download_list.remove(i)
            self.populate_dl_listbox()

        except:
            pass

    
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
        self.total_dl_size.set(lang['Total size:']+' ' + total_size)
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
        self.populate_selection_list()
        self.build_database()
        self.load_title_sizes()


    def get_output_directory(self):
        out_dir = filedialog.askdirectory()
        self.out_dir_box.delete('0', tk.END)
        self.out_dir_box.insert('end', out_dir)


    def load_program_revisions(self):
        print(lang['Checking for program updates, this might take a few seconds']+'.......\n')
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
            print(lang['COULD NOT CHECK FOR UPDATES'])
            print(lang['Check your internet connection or upgrade your Python to a version >= 3.6.4'])
            gui_data_set = ['/dojafoja/null/null/v{}'.format(__VERSION__)]

        gui_all = [__VERSION__]
    
        for i in gui_data_set:
            ver = LooseVersion(i.split('/')[4][1:-4])
            gui_all.append(ver)

        gui_newest = max(gui_all)
    
        if gui_newest > current_gui:
            self.notify_of_update()
        else:
            self.notify_of_update(update=False)

        self.versions['gui_all'] = [str(i) for i in gui_all]
        self.versions['gui_new'] = str(gui_newest)
        self.newest_gui_ver.set(gui_newest)


    def download_clicked(self, resuming=False):
        self.nb.select(self.progresstab)
        self.failed_box.configure(state='normal')
        self.failed_box.delete('0.0', 'end')
        self.failed_box.configure(state='disabled')
        self.thread1_status.set("")
        self.thread2_status.set("")
        self.thread3_status.set("")
        self.thread4_status.set("")
        self.thread5_status.set("")
        behavior = self.dl_behavior.get()
        if behavior == 2 and not resuming:
            if not message.askyesno(lang['Use fake tickets'], lang[('You have chosen to generate fake tickets for all titles '
                                                                    'except updates. Tickets will not be downloaded from the keysite. '
                                                                    'Would you like to continue anyway?')]):
                return
    
        rtry_count = self.retry_count.get()
        ptch_demo = self.patch_demo.get()
        ptch_dlc = self.patch_dlc.get()
        tick_only = self.tickets_only.get()
        sim = self.simulate_mode.get()
        
        joblist = []
        totalsize = 0
        self.flush_queues()
        
        RESULTQ.put(('log', '\n*** '+lang['Download session started:'].upper()+'  {} ***'.format(self.get_timestamp())))
        for i in self.download_list[:]:
            out_dir = self.output_dir.get().strip()
            t = i[1]
            k = i[2]
            td = self.title_dict.get(t, {})
            n = td.get('name', '').strip()
            if td.get('type', '').strip() == 'DEMO':
                n = n + '_Demo'
            r = td.get('region', '').strip()

            if behavior == 1:
                if t in self.has_ticket or td.get('type', '') == lang['Update'].upper():
                    k = None
                    ot = True
                else:
                    ot = False
            elif behavior == 2: # Always generate fake tickets, except updates. Could be useful if keysite is down.
                ot = False

            rslt = fnku.process_title_id(t, k, name=n, region=r, output_dir=out_dir, retry_count=rtry_count,
                                         onlinetickets=ot, patch_demo=ptch_demo, patch_dlc=ptch_demo, simulate=sim,
                                         tickets_only=tick_only, resultq=RESULTQ)
            if not rslt:
                if self.tickets_only.get():
                    return
                if self.simulate_mode.get(): # I use simulate mode often while developing.
                    return
                RESULTQ.put(('fail', '', t))
                return
            
            totalsize += rslt[1]
            self.download_list.remove(i)
            joblist.append(rslt[0])

        self.reset_progress()
        self.dl_total_float = totalsize
        self.dl_total_string.set(fnku.bytes2human(totalsize))
        self.progressbar['maximum'] = totalsize
        dlsession = DownloadSession(JOBQ, RESULTQ, ABORTQ, self.total_thread_count.get(), self)
        dlsession.populate_job(joblist)
        dlsession.poison_threads()
        self.active_thread_count = self.total_thread_count.get()
        self.download_button.configure(state='disabled')
        dlsession.start()
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

        
    def reset_progress(self):
        self.dl_progress = 0
        self.dl_progress_string.set('0')
        self.progressbar['maximum'] = 0
        self.progressbar['value'] = 0
        self.active_thread_count = 0
        self.failed_downloads = []


    def update_thread_status(self, status, finished=False):
        if finished:
            RESULTQ.put(('log', '*** '+lang['Download session completed'].upper()+':   {} ***'.format(self.get_timestamp())))
            self.thread1_status.set(lang['Download session completed'])
            self.thread2_status.set('')
            self.thread3_status.set('')
            self.thread4_status.set('')
            self.thread5_status.set('')
            return
        
        if status[1] == '1':
            self.thread1_status.set(lang['Thread']+' 1: {}'.format(status[2]))

        elif status[1] == '2':
            self.thread2_status.set(lang['Thread']+' 2: {}'.format(status[2]))

        elif status[1] == '3':
            self.thread3_status.set(lang['Thread']+' 3: {}'.format(status[2]))

        elif status[1] == '4':
            self.thread4_status.set(lang['Thread']+' 4: {}'.format(status[2]))

        elif status[1] == '5':
            self.thread5_status.set(lang['Thread']+' 5: {}'.format(status[2]))


    def get_timestamp(self):
        handle = datetime.now()
        ts = '{}/{}/{}  {}:{}.{}'.format(handle.year, handle.month, handle.day, handle.hour,
                                         handle.minute, handle.second)
        return ts


    def set_icon(self, window):
        icon = PhotoImage(file=os.path.join('images', 'icon.ppm'))
        window.tk.call('wm', 'iconphoto', window._w, icon)


    def process_result_queue(self):
        progress = 0
        results = []
        if not RESULTQ.empty():
            for i in range(RESULTQ.qsize()):
                results.append(RESULTQ.get())

                if results[i][0] == 'log':
                    self.log_box.configure(state='normal')
                    self.log_box.insert('end', results[i][1] + '\n')
                    self.log_box.configure(state='disabled')
                    self.log_box.see('end')
 
                elif results[i][0] == 'progress':
                    self.update_progress(results[i][1])
                    progress = 0
                    #progress += results[i][1]
 
                elif results[i][0] == 'status':
                    self.update_thread_status(results[i])
 
                elif results[i][0] == 'thread died':
                    self.active_thread_count -= 1
                    if not self.active_thread_count:
                        self.update_thread_status(('',''), finished=True)
                        self.download_button.configure(state='normal')
                        

                elif results[i][0] == 'fail':
                    if not results[i][2] in self.failed_downloads:
                        self.failed_downloads.append(results[i][2])
                        self.failed_box.configure(state='normal')
                        self.failed_box.insert('end', results[i][2] + '\n')
                        self.failed_box.configure(state='disabled')

                elif results[i][0] == 'aborted':
                    if not results[i][1] in self.aborted_downloads:
                        self.aborted_downloads.append(results[i][1])

            
            
            
        self.after(10, self.process_result_queue)  # Reschedule every .005 seconds


    def switch_language(self, *args):
        global lang
        lng = self.language.get()
        with open(os.path.join('data','language.json')) as f:
            oldlang = json.load(f)['language']
        if lng == 'english':
            lang = translations.english
            fnku.lang = translations.english
            themebuilder.lang = translations.english
    
        elif lng == 'spanish':
            lang = translations.spanish
            fnku.lang = translations.spanish
            themebuilder.lang = translations.spanish
            
        with open(os.path.join('data', 'language.json'), 'w') as f:
            setting = {'language': lng}
            json.dump(setting, f)
        if not oldlang == lng: # Only notify if new language is differeent than saved language
            message.showinfo(lang['Success'], lang['Restart application\nfor changes to take effect.'])

        
    def get_gui_language(self):
        return lang

   
    def set_theme(self,*args):
        sel_theme = self.selected_theme.get()
        if len(args) < 3:
            self.themes['USER DEFINED'] = args[0]
            sel_theme = 'USER DEFINED'
        else:
            try:
                t = self.themes[sel_theme]
                themebuilder.set_record(t.copy())
            except Exception as e:
                print(e)

        main = rgb_to_hex(self.themes[sel_theme].get("main", None))
        maintext = rgb_to_hex(self.themes[sel_theme].get("maintext", None))
        box = rgb_to_hex(self.themes[sel_theme].get("box", None))
        boxtext = rgb_to_hex(self.themes[sel_theme].get("boxtext", None))
        button = rgb_to_hex(self.themes[sel_theme].get("button", None))
        buttontext = rgb_to_hex(self.themes[sel_theme].get("buttontext", None))
        buttonhover = rgb_to_hex(self.themes[sel_theme].get("buttonhover", None))
        buttontexthover = rgb_to_hex(self.themes[sel_theme].get("buttontexthover", None))
        tab = rgb_to_hex(self.themes[sel_theme].get("tab", None))
        tabtext = rgb_to_hex(self.themes[sel_theme].get("tabtext", None))
        tabhover = rgb_to_hex(self.themes[sel_theme].get("tabhover", None))
        tabtexthover = rgb_to_hex(self.themes[sel_theme].get("tabtexthover", None))

        if not main: 
            main = 'light gray'
        if not maintext:
            maintext = 'black' 
        if not box:
            box = 'white'
        if not boxtext:
            boxtext = 'black'
        if not button:
            button = 'light gray'
        if not buttontext:
            buttontext = 'black'
        if not buttonhover:
            buttonhover = button
        if not buttontexthover:
            buttontexthover = buttontext
        if not tab:
            tab = 'light gray'
        if not tabtext:
            tabtext = 'black'
        if not tabhover:
            tabhover = tab
        if not tabtexthover:
            tabtexthover = tabtext
            
            
        self.custom_entry_style.configure("EntryStyle.TEntry", foreground=boxtext, fieldbackground=box)       
        self.configure(background=main)
        self.selection_box.configure(background=box, foreground=boxtext)
        self.dl_listbox.configure(background=box, foreground=boxtext)
        self.log_box.configure(background=box, foreground=boxtext)
        self.failed_box.configure(background=box, foreground=boxtext)
        self.throttler.configure(background=main, foreground=maintext, highlightthickness=0)
        ttk.Style().configure("TFrame", background=main)
        ttk.Style().configure("TLabel", background=main, foreground=maintext)
        ttk.Style().configure("TCheckbutton", background=main, foreground=maintext, active=main)
        ttk.Style().configure("TRadiobutton", background=main, foreground=maintext)
        ttk.Style().configure("TNotebook", background = main)
        ttk.Style().configure("TScale", background=main)
        ttk.Style().map("TCheckbutton", background=[("active", main)], foreground=[("active", maintext)])
        ttk.Style().map("TRadiobutton", background=[("active", main)], foreground=[("active",maintext)])
        ttk.Style().map("TCombobox", background=[("active", box)], foreground=[("active",boxtext)],
                        fieldbackground=[("readonly", box)])
        
        if os.name == 'posix':
            ttk.Style().configure("TCombobox", fieldbackground=box, foreground=boxtext)
            ttk.Style().configure("TButton", background=button, foreground=buttontext)
            ttk.Style().map("TButton", background=[("active", buttonhover)], foreground=[("active",buttontexthover)])
            ttk.Style().configure("TNotebook.Tab", background = tab, foreground = tabtext)
            ttk.Style().map("TNotebook.Tab", background=[("selected", main), ("active", tabhover)],
                            foreground=[("selected", maintext), ("active", tabtexthover)])


    def show_theme_frame(self):
        if self.theme_frame_open: # Only allow 1 theme frame Toplevel instance at a time.
            return
        tl = tk.Toplevel()
        tl.title('FunKii-UI Theme Builder')
        tl.protocol("WM_DELETE_WINDOW", lambda: self.on_theme_frame_destroy(tl))
        self.set_icon(tl)
        f = themebuilder.Root(app=self, master=tl)
        self.theme_frame_open = True


    def on_theme_frame_destroy(self, tl):
        tl.destroy()
        self.theme_frame_open = False


    def save_custom_theme(self, themename, usertheme):
        if not len(themename):
            message.showerror(lang['Error'], lang['Please provide a name to save this theme.'])
            return
        
        x = self.load_themes()
        x[themename] = usertheme
        self.selected_theme.set(themename)
        
        with open(os.path.join('data', 'themes.json'), 'w') as f:
            json.dump(x, f)
            
        x = [i for i in x]
        x.sort()
        self.theme_selector.configure(values=x)


    def load_gui_vars(self):
        from modules.custom import gui_vars
        gui_vars.load_vars(self)


    def load_themes(self):
        with open(os.path.join('data', 'themes.json')) as f:
            return json.load(f)


    def abort_download_session(self):
        ABORTQ.put(None) # Download will abort if the ABORTQ contains anything in it.
        message.showinfo(lang['Download stopped'], lang[('You have forced the download to stop. You can redownload any of the titles '
                                                       'that were downloading and they will resume from the exact byte where they stopped.')])
        #self.download_button.configure(state='normal')


    def resume_download_session(self):
        self.add_to_list(self.failed_downloads, batch=True)
        self.download_clicked()
        
        #print('dlprogress',self.dl_progress)
        #print('q size', JOBQ.qsize())
        #self.failed_downloads = []
        #self.flush_queues()
        #dlsession = DownloadSession(JOBQ, RESULTQ, ABORTQ, self.total_thread_count.get(), self)
        #dlsession.populate_job(((self.aborted_downloads,)))
        
        #dlsession.poison_threads()
        #self.active_thread_count = self.total_thread_count.get()
        #self.download_button.configure(state='disabled')
        #dlsession.start_session()
        

    def flush_queues(self):
        for i in (ABORTQ, RESULTQ, JOBQ):
            for each in range(i.qsize()):
                _ = i.get()



        
        
def rgb_to_hex(rgb):
    if rgb:
        if rgb.startswith("("):
            rgb = eval(rgb)
            rgb = "#%02x%02x%02x" % rgb

    return rgb



if __name__ == '__main__':
    root = RootWindow()
    root.title('ACO WUP DOWLOADER 3.0.0')
    root.minsize(850, 400)
    root.geometry("1020x{}+0+0".format(root.winfo_screenheight() - 80))
    root.set_icon(root)
    root.after(1000, root.process_result_queue)
    root.mainloop()
    root.save_settings()
