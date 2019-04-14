try:
    from Tkinter import StringVar, IntVar, BooleanVar
except ImportError:
    from tkinter import StringVar, IntVar, BooleanVar
import json, os

def load_vars(gui):
    gui.language = StringVar()
    gui.language.trace('w', gui.switch_language)
    with open(os.path.join('data','language.json'), 'r') as f:
        gui.language.set(json.load(f)['language'])
    lang = gui.get_gui_language()

    gui.failed_downloads = []
    gui.aborted_downloads = []
    gui.download_list = []
    gui.selection_list = []
    gui.title_data = []
    gui.themes = gui.load_themes()    
    gui.output_dir = StringVar()
    gui.retry_count = IntVar(value=3)
    gui.patch_demo = BooleanVar(value=True)
    gui.patch_dlc = BooleanVar(value=True)
    gui.tickets_only = BooleanVar(value=False)
    gui.simulate_mode = BooleanVar(value=False)
    gui.filter_usa = BooleanVar(value=True)
    gui.filter_eur = BooleanVar(value=True)
    gui.filter_jpn = BooleanVar(value=True)
    gui.filter_game = BooleanVar(value=True)
    gui.filter_dlc = BooleanVar(value=True)
    gui.filter_update = BooleanVar(value=True)
    gui.filter_demo = BooleanVar(value=True)
    gui.filter_system = BooleanVar(value=True)
    gui.filter_hasticket = BooleanVar(value=False)
    gui.show_batch = BooleanVar(value=False)
    gui.dl_behavior = IntVar(value=1)
    gui.fetch_dlc = BooleanVar(value=True)
    gui.fetch_updates = BooleanVar(value=True)
    gui.auto_fetching = StringVar(value='prompt')
    gui.fetch_on_batch = BooleanVar(value=False)
    gui.batch_op_running = BooleanVar(value=False)
    gui.total_dl_size = StringVar(value=lang['Total size:'])
    gui.total_dl_size_warning = StringVar()
    gui.dl_progress = 0
    gui.dl_progress_string = StringVar()
    gui.dl_progress_string.set('0')
    gui.dl_total_string = StringVar()
    gui.dl_total_string.set('0')
    gui.dl_total_float = 0
    gui.dl_percentage_string = StringVar()
    gui.dl_percentage_string.set('0.00%')
    gui.dl_speed = StringVar()
    gui.active_thread_count = 0
    gui.thread1_status = StringVar()
    gui.thread2_status = StringVar()
    gui.thread3_status = StringVar()
    gui.thread4_status = StringVar()
    gui.thread5_status = StringVar()
    gui.total_thread_count = IntVar()
    gui.dl_warning_msg = lang[("! You have one or more items in the list with an unknown size.\nThis may mean that the "
                                "title is not available.")]
    gui.idvar = StringVar()
    gui.idvar.trace('w', gui.id_changed)
    gui.download_data_on_start = BooleanVar(value=False)
    gui.newest_gui_ver = StringVar()
    gui.newest_fnku_ver = StringVar()
    gui.user_search_var = StringVar()
    gui.user_search_var.trace('w', gui.user_search_changed)
    gui.selected_theme = StringVar()
    gui.selected_theme.trace('w', gui.set_theme)
    gui.usa_selections = {'game': [], 'dlc': [], 'update': [], 'demo': [], 'system': []}
    gui.eur_selections = {'game': [], 'dlc': [], 'update': [], 'demo': [], 'system': []}
    gui.jpn_selections = {'game': [], 'dlc': [], 'update': [], 'demo': [], 'system': []}
    gui.title_sizes_raw = {}
    gui.title_sizes = {}
    gui.reverse_title_names = {}
    gui.title_dict = {}
    gui.has_ticket = []
    gui.errors = 0
    gui.raw_titlecount = 0
    gui.theme_frame_open = False


