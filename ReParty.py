from queue import Queue, Empty
from threading import Thread
from time import time
from PIL import Image, ImageTk
from Helpers import Cleaner, font_verdana, dialog_modal, lister
from Filepaths import *
from tkinter import Tk, Menu, Entry, Label, Button, Listbox, Frame, StringVar, IntVar
# importing common UI elements and tk for CONSTANTS
import tkinter as tk
import tkinter.ttk as ttk
from SettingsModal import SettingsModal
from QueryResultsDashboard import QueryResultsDashboard
from GameVars import game_result_list, venue_list, mission_list
from ReplayParser import ReplayParser
from os import listdir

ROLE_EITHER = 'both'
ROLE_SNIPER = 'sniper'
ROLE_SPY = 'spy'

MWC_EITHER = 'Either'
# might be desirable
# MWC_EXTRA = 'Overcompleted'
MWC_YES = 'Yes'
MWC_NO = 'No'


class ReParty(Tk):
    def __init__(self, VENUE_DISPLAY_WIDTH=6):
        Tk.__init__(self)
        self.title('ReParty')
        self.minsize(width=640, height=480)
        self.iconbitmap(default=ASSETS / 'diamond.ico')
        self.protocol('WM_DELETE_WINDOW', self.on_window_close)
        self._loaded_images = {}  # holds images in memory so they aren't garbage collected

        # might as well persist per session rather than per query, if the intent is to avoid recleaning multiple times
        self.cleaner = Cleaner(lambda user: user.lower().replace(' ', ''))

        toolbar = Menu(self)
        self.config(menu=toolbar)
        menu_file = Menu(toolbar, tearoff=0)
        menu_file.add_command(label="Settings", command=lambda: SettingsModal().mainloop())
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.on_window_close)
        toolbar.add_cascade(label="Menu", menu=menu_file)

        (container := Frame(self)).pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.player_left, self.player_right = StringVar(), StringVar()
        self.progress = IntVar()
        self.query_in_progress = False
        self.displayed_venues = list(filter(lambda ven: ven.selected, venue_list))

        (players_frame := Frame(self)).pack()
        Label(players_frame, text="Players:", width=7).pack(side=tk.LEFT)
        player_entry = Entry(players_frame, textvariable=self.player_left, width=35)
        player_entry.bind('<Return>', lambda event: self.submit_query())
        player_entry.pack(side=tk.LEFT)
        Button(players_frame, text="vs", command=self.swap_players, width=2).pack(side=tk.LEFT, padx=6)
        player_entry = Entry(players_frame, textvariable=self.player_right, width=35)
        player_entry.bind('<Return>', lambda event: self.submit_query())
        player_entry.pack(side=tk.LEFT)
        Label(players_frame, text="as", width=2).pack(side=tk.LEFT)
        self.combo_role = ttk.Combobox(players_frame, values=[ROLE_EITHER, ROLE_SNIPER, ROLE_SPY], width=6)
        self.combo_role.pack(side=tk.LEFT)
        self.combo_role.set(ROLE_EITHER)

        self.submission = Button(players_frame, text='Submit', command=self.submit_query)
        self.submission.pack(side=tk.RIGHT)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack()

        (venues_frame := Frame(self.tabs)).pack()
        self.tabs.add(venues_frame, text='  Venues  ')

        self.__venue_buttons = {}
        self.__loaded_images = {}
        for i, venue in enumerate(self.displayed_venues):
            normal = Image.open(venue.get_image_path()).resize((160, 90), Image.ANTIALIAS)
            thumb_color = ImageTk.PhotoImage(normal)
            thumb_grey = ImageTk.PhotoImage(normal.convert('LA'))
            self.__loaded_images[venue] = thumb_grey, thumb_color
            (v_butt := Button(
                venues_frame,
                command=lambda v=i: self.toggle_venue(v), width=160, height=90,
                image=self.__loaded_images[venue][venue.selected], text=f"\n\n\n{venue.name}", compound=tk.CENTER,
                background='#0a0' if venue.selected else '#a00', foreground='white', font=font_verdana(13)
            )).grid(row=i // VENUE_DISPLAY_WIDTH, column=i % VENUE_DISPLAY_WIDTH)
            self.__venue_buttons[venue] = v_butt

        # todo this shall be replaced... v2: per venue A/B selection
        # i = len(self.displayed_venues)
        # (setup_frame := Frame(venues_frame)).grid(
        #     row=i // self.VENUE_DISPLAY_WIDTH, column=i % self.VENUE_DISPLAY_WIDTH,
        #     columnspan=5 - (i % self.VENUE_DISPLAY_WIDTH))  # todo why 5
        # Label(setup_frame, text='Any', font=font_verdana(12)).pack(side=LEFT, padx=2, pady=2)
        # (scroll_setup_any := Spinbox(setup_frame, font=font_verdana(11), values=[c for c in "X12345678"],
        #                              command=self.validate_setup, width=2)).pack(side=LEFT, pady=2)
        # scroll_setup_any.set("X")
        # self.scroll_setup_any = scroll_setup_any
        # Label(setup_frame, text='/', font=font_verdana(12), width=1).pack(side=LEFT)
        # (scroll_setup_of := Spinbox(setup_frame, font=font_verdana(11), values=[c for c in "X12345678"],
        #                             command=self.validate_setup, width=2)).pack(side=LEFT)
        # scroll_setup_of.set("X")
        # self.scroll_setup_of = scroll_setup_of

        settings_frame = Frame(self.tabs)
        settings_frame.pack()
        self.tabs.add(settings_frame, text='  Settings  ')

        Label(settings_frame, text='Missions Completed').grid(row=1, column=1, sticky=tk.W, padx=6)
        self.listbox_missions = Listbox(
            settings_frame, selectmode="multiple", exportselection=False, width=25, height=8)
        self.listbox_missions.grid(row=2, rowspan=8, column=1, sticky=tk.W + tk.N, padx=6)
        self.populate_listbox(self.listbox_missions, mission_list)

        Label(settings_frame, text='Game Results').grid(row=1, column=3, columnspan=2, sticky=tk.W, padx=6)
        self.listbox_results = Listbox(
            settings_frame, selectmode="multiple", exportselection=False, width=25, height=4)
        self.listbox_results.grid(row=2, rowspan=4, column=3, columnspan=2, sticky=tk.W + tk.N, padx=6)
        self.populate_listbox(self.listbox_results, game_result_list)

        Label(settings_frame, text='Reaches MWC?').grid(row=6, column=3, sticky=tk.W, padx=6)
        self.combo_mwc = ttk.Combobox(settings_frame, values=[MWC_EITHER, MWC_YES, MWC_NO], width=6)
        self.combo_mwc.grid(row=6, column=4, sticky=tk.W, padx=6)
        self.combo_mwc.set(MWC_EITHER)

        Label(settings_frame, text='Replay Directories').grid(row=1, column=5, sticky=tk.W, padx=6)
        self.listbox_directories = Listbox(
            settings_frame, selectmode=tk.MULTIPLE, exportselection=False, width=25, height=8)
        self.listbox_directories.grid(row=2, rowspan=8, column=5, columnspan=2, sticky=tk.W + tk.N, padx=6)
        subdirectories = listdir(REPLAYS_DIRECTORY())
        # todo if len(subdirs) > 8, add scrollbar
        self.populate_listbox(self.listbox_directories, subdirectories)
        for default_dir in ('Matches', 'Spectations'):
            self.listbox_directories.selection_set(subdirectories.index(default_dir))

        self.progress_bar_style = ttk.Style(self)
        self.progress_bar_style.layout(
            "LabeledProgressbar", [
                ('LabeledProgressbar.trough', {'children': [
                    ('LabeledProgressbar.pbar', {'side': 'left', 'sticky': 'ns'}),
                    ("LabeledProgressbar.label", {"sticky": "e"})
                ], 'sticky': 'nswe'})]
        )
        # self.progress_bar_style.configure('LabeledProgressbar', bg='green')  # todo figure out bar color
        self.loading_bar = ttk.Progressbar(self, variable=self.progress, maximum=1, style='LabeledProgressbar')
        self.loading_bar.pack(side=tk.BOTTOM, fill=tk.X)

    @staticmethod
    def populate_listbox(box, options):
        for option in options:
            box.insert(tk.END, option)

    def set_status(self, text):
        self.progress_bar_style.configure("LabeledProgressbar", text=text)

    def on_window_close(self):
        REPARTY_CONFIG.save()
        self.destroy()

    def toggle_venue(self, venue_index):
        venue = self.displayed_venues[venue_index]
        val = not venue.selected
        self.__venue_buttons[venue].configure(
            image=self.__loaded_images[venue][val],
            background='#0a0' if val else '#a00'
        )
        venue.selected = val

    def swap_players(self):
        temp = self.player_left.get()
        self.player_left.set(self.player_right.get())
        self.player_right.set(temp)

    def validate_setup(self):  # todo finish behavior, may require persistent variables to determine the change
        setup_any = self.scroll_setup_any.get()
        setup_of = self.scroll_setup_of.get()
        if "X" in {setup_any, setup_of}:
            return  # only matters when both values are set
        if setup_any > setup_of:
            self.scroll_setup_of.set(setup_any)

    def submit_query(self):
        left_player = self.cleaner.clean(self.player_left.get())
        right_player = self.cleaner.clean(self.player_right.get())
        role_match = self.combo_role.get()
        # print(left_player, right_player, role_match)

        # todo v2 allow multiple player search, but for v1 just one plz
        # left_players, right_players = ({
        #     sanitized for pl in group.get().split(",")
        #     if (sanitized := cleaner.clean(pl))
        # } for group in (self.player_left, self.player_right))

        criteria = []
        if left_player and right_player:
            if role_match == ROLE_EITHER:
                criteria.append(lambda replay: right_player in self.cleaner.clean(replay.spy + replay.sniper))
                criteria.append(lambda replay: left_player in self.cleaner.clean(replay.spy + replay.sniper))
            elif role_match == ROLE_SNIPER:
                criteria.append(lambda replay: right_player in self.cleaner.clean(replay.sniper))
                criteria.append(lambda replay: left_player in self.cleaner.clean(replay.spy))
            elif role_match == ROLE_SPY:
                criteria.append(lambda replay: right_player in self.cleaner.clean(replay.spy))
                criteria.append(lambda replay: left_player in self.cleaner.clean(replay.sniper))
        elif right_player:
            if role_match == ROLE_EITHER:
                criteria.append(lambda replay: right_player in self.cleaner.clean(replay.spy + replay.sniper))
            elif role_match == ROLE_SNIPER:
                criteria.append(lambda replay: right_player in self.cleaner.clean(replay.sniper))
            elif role_match == ROLE_SPY:
                criteria.append(lambda replay: right_player in self.cleaner.clean(replay.spy))
        elif left_player:
            if role_match == ROLE_EITHER:
                criteria.append(lambda replay: left_player in self.cleaner.clean(replay.spy + replay.sniper))
            elif role_match == ROLE_SNIPER:
                criteria.append(lambda replay: left_player in self.cleaner.clean(replay.spy))
            elif role_match == ROLE_SPY:
                criteria.append(lambda replay: left_player in self.cleaner.clean(replay.sniper))
        # role_match is only relevant if one or more players are specified

        # if (setup_any := self.scroll_setup_any.get()) != "X":
        #     criteria.append(lambda rep: rep.setup[1] == setup_any)
        # if (setup_of := self.scroll_setup_of.get()) != "X":
        #     criteria.append(lambda rep: rep.setup[3] == setup_of)

        if venues_wanted := {v.name for v in self.displayed_venues if v.selected}:
            if len(venues_wanted) < len(self.displayed_venues):  # don't add a criteria if any venue is ok
                criteria.append(lambda rep: rep.venue in venues_wanted)
        else:
            dialog_modal("No venues selected.", "Please select at least one venue and try again.")
            return

        if not (directories_wanted := [
            self.listbox_directories.get(i) for i in self.listbox_directories.curselection()
        ]):
            dialog_modal("No directories selected.", "Please select at least one directory to search and try again.")
            return

        # if missions_wanted:
        #     criteria.append(lambda rep: len(missions_wanted - rep["completed_missions"]) == 0)
        if results_wanted := {game_result_list[i] for i in self.listbox_results.curselection()}:
            criteria.append(lambda replay: replay.result in results_wanted)

        mwc_match = self.combo_mwc.get()
        if mwc_match == MWC_YES:
            criteria.append(lambda replay: len(replay.completed_missions) >= int(replay.setup[1]))
        elif mwc_match == MWC_NO:
            criteria.append(lambda replay: len(replay.completed_missions) < int(replay.setup[1]))

        print(len(criteria), 'criteria applied')
        self.begin_query(criteria, directories_wanted)

    def begin_query(self, criteria, directories):
        # todo with my improved threading knowledge, turn the disabled submit button into a cancel button!
        if self.query_in_progress:
            return
        self.query_in_progress = True
        self.submission['state'] = tk.DISABLED  # prevent another load until the previous one has finished

        replays = []
        hummus = ReplayParser()
        replay_dir = REPLAYS_DIRECTORY()
        for subdir in directories:
            # This part is relatively fast, so it is done first to set up the progress bar.
            replays.extend(hummus.find_replays(replay_dir / subdir))
        if not (count := len(replays)):
            dialog_modal("Alert!", f"No replays were found in your {lister(directories)} folder(s).")
            self.submission['state'] = tk.NORMAL
            return

        using_progress_bar = REPARTY_CONFIG[KEYWORD_PROGRESS_BAR]
        self.progress.set(0)

        def __threaded_parsing(output: Queue):
            if using_progress_bar:
                start = time()
                blank = f'Matched %d / {count} (%d:%02d elapsed) '
                self.loading_bar.configure(maximum=count)

                results = []
                i = 0
                t = 1
                while i < count:
                    while i < count and time() - start < t:  # 1 second intervals
                        try:
                            parsed = hummus.parse(replays[i])
                            if all(criterion(parsed) for criterion in criteria):
                                results.append(parsed)
                        except ReplayParser.ReplayParseException as e:
                            print(e)
                        i += 1
                    # Remnant of v0, I don't remember what it does so hopefully it's not important... (lmao)
                    # self.update_idletasks()

                    self.set_status(blank % (len(results), t // 60, t % 60))
                    self.progress.set(i)
                    t += 1
                output.put(results)
            else:
                self.set_status(f'Parsing {count} replays... ')
                results = []
                for replay in replays:
                    try:
                        parsed = hummus.parse(replay)
                        if all(crit(parsed) for crit in criteria):
                            results.append(parsed)
                    except ReplayParser.ReplayParseException as er:
                        print(er)
                output.put(results)

        q = Queue()
        Thread(target=lambda: __threaded_parsing(q), daemon=True).start()  # Damon finally does something useful!
        # todo this doesn't have to be daemon?

        def __thread_finished_check():
            try:
                results = q.get_nowait()
                self.submission['state'] = tk.NORMAL
                self.query_in_progress = False
                if results:
                    self.set_status(f'{len(results)} Replays Found')
                    QueryResultsDashboard(results).mainloop()
                else:
                    self.set_status('No Replays Found')
            except Empty:  # the Queue has not had results inserted yet, wait longer
                self.after(1000, __thread_finished_check)

        self.after(1500, __thread_finished_check)


def main():
    try:
        ReParty().mainloop()
    except Exception as e:
        REPARTY_CONFIG['CRASH REPORT'] = str(e)
        REPARTY_CONFIG.save()
        dialog_modal(
            'ReParty Crashed!',
            'Please open your ReParty_config.json file and forward the "CRASH REPORT" to Legorve Genine#3815')


if __name__ == '__main__':
    # pyinstaller --add-data './assets;assets' -n 'ReParty v1.1' -w -F RePartyApplication.py
    main()