# -*- coding: utf-8 -*-

import json
import sys
import os

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox as message
    from tkinter import filedialog 

except ImportError:
    import Tkinter as tk
    import ttk
    import tkMessageBox as message
    import tkFileDialog as filedialog

class Root(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.existing_entries = []
        self.source_data = []
        self.all_versions = []
        self.namelist = []
        self.duplicatenames = []
        
        f1 = ttk.Frame(self)
        f2 = ttk.Frame(self)
        f3 = ttk.Frame(self)
        f4 = ttk.Frame(self)
        f5 = ttk.Frame(self)

        self.active_selection = tk.StringVar()
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        sel_scroller = ttk.Scrollbar(f1, orient='vertical')
        self.existing_entries_box = tk.Listbox(f1)  
        self.existing_entries_box.pack(padx=1, pady=10, side='left', fill='both', expand=True)
        self.existing_entries_box.bind('<<ListboxSelect>>', self.populate_field_values)
        sel_scroller.pack(side='left', fill='y')
        sel_scroller.config(command=self.existing_entries_box.yview)
        self.existing_entries_box.config(yscrollcommand=sel_scroller.set)
        self.existing_entries_box.config(exportselection=False)
        self.name_box = ttk.Entry(f2, width=70)
        self.region_box = ttk.Combobox(f2, width=4, values=['USA','EUR','JPN'], state='readonly')
        self.category_box = ttk.Combobox(f2, width=5, values=['nes','snes','gba','n64','nds','gc','wii'], state='readonly')
        self.url_box = ttk.Entry(f2, width=70)
        ttk.Label(f2, text='Name:').pack(padx=10, side='top', anchor='w')
        self.name_box.pack(padx=10, pady=10, side='top', anchor='w')
        ttk.Label(f2, text='Url:').pack(padx=10, side='top', anchor='w')
        self.url_box.pack(padx=10,pady=10,side='top', anchor='w')
        ttk.Label(f2, text='Category:').pack(padx=10, side='top', anchor='w')
        self.category_box.pack(padx=10,pady=10,side='top', anchor='w')
        ttk.Label(f2, text='Region:').pack(padx=10, side='top', anchor='w')
        self.region_box.pack(padx=10, pady=10, side='top', anchor='w')
        ttk.Button(f2, text='Create new item', width=30, command= self.create_new_item).pack(padx=3, pady=15, side='top')
        ttk.Button(f2, text='Update selected item', width=20,command=self.update_selected_item).pack(padx=3, pady=15, side='top')
        ttk.Button(f2, text='Remove selected item', width=20, command= self.remove_from_sources).pack(padx=3, pady=15, side='top')
        ttk.Button(f2, text='Mergefiles', width=20, command= self.merge_files).pack(padx=3, pady=15, side='top')
        tk.Button(f2, text='Save', borderwidth=5, width=10, height=1, bg='light grey', font='Helvetica 20 bold',
                  command=self.save_to_file).pack(padx=3, pady=25)
        #ttk.Label
        ttk.Label(f3, text='Selected item:', font='Helvetica 10 bold').pack(side='left', padx=5, pady=3)
        ttk.Label(f4, textvariable=self.active_selection, font='Helvetica 10 bold').pack(side='left', padx=10, pady=10)
        ttk.Label(f5, text='SOURCES VERSION:', font='Helvetica 12 bold').pack(side='left', padx=10, pady=10)
        self.version_box = ttk.Entry(f5, width=5)
        self.version_box.pack(side='left', padx=10, pady=10)
        ttk.Button(f5, text='Update version', command=self.update_version_number).pack(side='left', padx=10, pady=10)
        
        f1.grid(column=1, row=1, columnspan=3, rowspan=2, sticky='nsew')
        f2.grid(column=4, row=1, columnspan=2, sticky='n')
        f3.grid(column=1, row=3, sticky='w')
        f4.grid(column=1, row=4, columnspan=2, sticky='w')
        f5.grid(column=4, row=3, sticky='e')    
        
        self.load_source_data()
        self.populate_sources_box()
        self.insert_version()


    def insert_version(self):
        self.version_box.delete('0', tk.END)
        self.version_box.insert('0', max(self.all_versions))


    def strip_versions(self):
        for i in self.source_data[:]:
            if i['name'] == 'VERSION':
                self.source_data.remove(i)
                
    def get_version(self):
        for i in self.source_data:
            if i['name'] == 'VERSION':
                return i['version']

   
    def load_source_data(self, fileslist=None):
        if not fileslist:
            fileslist = ['customsources.json']
        for i in fileslist:
            if sys.version_info[0] == 3:
                try:
                    with open(i, encoding='utf-8') as f:
                        data = json.load(f)
                except UnicodeDecodeError:
                    with open(i, encoding='latin-1') as f:
                        data = json.load(f)
            else:
                try:
                    with open(i) as f:
                        data = json.load(f, 'utf-8')
                except UnicodeDecodeError:
                    with open(i) as f:
                        data = json.load(f, 'latin-1')
                    
            for i in data[:]:
                if i['name'].strip() == '':
                    data.remove(i)
                if i['name'] == 'VERSION':
                    self.source_data.append(i)
                    self.all_versions.append(i['version'])

            for i in data:
                if not i['name'] == 'VERSION':
                    if not i['name'] in self.namelist:
                        self.source_data.append(i)
                        self.namelist.append(i['name'])
                    else:
                        self.duplicatenames.append(i)
                
        #self.source_data = data

        
    def populate_sources_box(self):
        self.existing_entries_box.delete('0', tk.END)
        
        for i in self.source_data:
            if not i['name'] == '':
                if not i['name'] == 'VERSION':
                    self.existing_entries_box.insert(tk.END, i['name'])


    def remove_from_sources(self):
        name = self.active_selection.get()
        
        for i in self.source_data[:]:
            if i['name'] == name:
                self.source_data.remove(i)

        self.active_selection.set('')        
        self.populate_sources_box()


    def populate_field_values(self, event):
        w = event.widget
        try:
            name = w.get(w.curselection()[0])
            self.active_selection.set(name)
            
            for i in self.source_data:
                if i['name'] == name:
                    category = i['category']
                    region = i['region']
                    url = i['url']
                    break
                
            self.name_box.delete('0', tk.END)
            self.name_box.insert('0', name)
            self.url_box.delete('0', tk.END)
            self.url_box.insert('0', url)
            self.region_box.set(region)
            self.category_box.set(category)
        except:
            pass

    def update_version_number(self):
        ver = self.version_box.get().strip()
        for i in self.source_data[:]:
            if i['name'] == 'VERSION':
                i['version'] = ver
                self.save_to_file()
                return
            
        version = {'name': 'VERSION', 'version': ver}
        self.source_data.append(version)
        self.save_to_file()
                
        
    def update_selected_item(self):
        index = self.existing_entries_box.curselection()
        name = self.active_selection.get()
        for i in self.source_data:
            if i['name'] == name:
                for entry in self.source_data:
                    if self.name_box.get() == entry['name']:
                        if entry['name'] != self.active_selection.get(): #Duplicate entry
                            message.showerror('Duplicate name', 'Do not use duplicate names for custom sources!')
                            return
                        
                newname = self.name_box.get()
                url = self.url_box.get()
                region = self.region_box.get()
                category = self.category_box.get()

                for each in (newname, url, region, category):
                    if each == '':
                        message.showerror('Empty value', 'One or more value fields are empty!')
                        return
                        
                i['name'] = self.name_box.get()
                i['url'] = self.url_box.get()
                i['region'] = self.region_box.get()
                i['category'] = self.category_box.get()
                self.active_selection.set(i['name'])
                break
            
        self.populate_sources_box()
        self.existing_entries_box.selection_set(index)      

    def create_new_item(self):
        name = self.name_box.get()
        
        for i in self.source_data:
            if i['name'] == name:
                message.showerror('Duplicate name', 'Do not use duplicate names for custom sources!')
                return
        url = self.url_box.get()
        region = self.region_box.get()
        category = self.category_box.get()
        
        for i in (name, url, region, category): # Checking for blank entries
            if i == '':
                message.showerror('Empty value', 'One or more value fields are empty!')
                return
                
        item = {'name': name, 'url': url, 'region': region, 'category': category}
        self.source_data.append(item)
        self.populate_sources_box()
        self.active_selection.set(name)
        self.existing_entries_box.selection_set(tk.END)

        
    def save_to_file(self, outname=None):
        if not outname:
            outname = 'customsources.json'
            jsonstring = self.get_formatted_json()
        else:
            outname = self.get_duplicates_filename(outname)
            jsonstring = self.get_formatted_json(source=self.duplicatenames)
        
        if sys.version_info[0] == 3:
            try:
                with open(outname, 'w', encoding='utf-8') as f:
                    f.write(jsonstring)
                    message.showinfo('Success', 'Succesfully saved customsources.json')
            except UnicodeDecodeError:
                with open(outname, 'w', encoding='latin-1') as f:
                    f.write(jsonstring)
                    message.showinfo('Success', 'Succesfully saved customsources.json')
        else:
            try:
                with open(outname, 'w') as f:
                    f.write(jsonstring)
                    message.showinfo('Success', 'Succesfully saved customsources.json')
            except UnicodeDecodeError:
                with open(outname, 'w') as f:
                    f.write(jsonstring)
                    message.showinfo('Success', 'Succesfully saved customsources.json')


    def get_formatted_json(self, source=None):
        if not source:
            source = self.source_data
            
        if sys.version_info[0] == 3:
            raw = json.dumps(source, sort_keys=True)

        else:
            try:
                raw = json.dumps(source, 'utf-8', sort_keys=True)
            except UnicodeDecodeError:
                raw = json.dumps(source, 'latin-1', sort_keys=True)
                
        parsed = []

        # Parse the json output into a list and apply a styled formatting. 
        # It's kind of ugly but it works ok! Hahaha
        for i in enumerate(raw):
            if i[0] == 0:
                parsed.append(i[1]+'\n\n')
                
            elif i[0]+ 1 == len(raw):
                parsed.append('\n\n'+i[1])

            elif i[1] == ',':
                if raw[(i[0] - 1)] == '}':
                    parsed.append(i[1]+'\n\n')
                else:
                    parsed.append(i[1])

            elif i[1] == ' ':
                if raw[(i[0] + 1)] == '{':
                    pass
                else:
                    parsed.append(i[1])
            else:
                parsed.append(i[1])
                
        jsonstring = ''.join(parsed)
        return (jsonstring)    
        

    def get_duplicates_filename(self,dupe):
        dupename, ext  = os.path.splitext(dupe)
        incrementer = 2
        while True:
            if os.path.isfile(dupename + ext):
                dupename = '{}{}'.format(dupename, incrementer)
                incrementer += 1
            else:
                return '{}{}'.format(dupename, ext)
    
    def merge_files(self):
        fileset = list(filedialog.askopenfilenames())
        originalsource = os.path.join(os.getcwd(), 'customsources.json')
        if originalsource in fileset:
            fileset.remove(originalsource)
            
        self.load_source_data(fileslist=fileset)
        self.strip_versions()
        self.insert_version()
        self.update_version_number()
        self.source_data = []
        self.namelist = []
        self.load_source_data()
        self.populate_sources_box()
        if len(self.duplicatenames) > 0:
            self.save_to_file('duplicates.json')
            message.showerror('Error', ('Duplicate names were found in the sources! They have been\nremoved and dumped to a duplicates file.'
                                        'You can alter the names in this file to be unique\nand merge the duplicates file back in.'))
            

        

if __name__ == '__main__':
    root = Root()
    root.title('Manage Custom Sources')
    root.minsize(850,400)
    root.mainloop()
