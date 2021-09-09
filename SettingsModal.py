from tkinter import Tk, StringVar, BooleanVar, filedialog, Label, Entry, Button, Checkbutton, E as EAST, W as WEST
from Filepaths import REPARTY_CONFIG, KEYWORD_GAME_DIR, KEYWORD_PROGRESS_BAR


class SettingsModal(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('ReParty: Settings')
        self.protocol('WM_DELETE_WINDOW', self.destroy)  # todo currently exits without saving, should ask for confirm

        self.sp_dir = StringVar(self, value=REPARTY_CONFIG[KEYWORD_GAME_DIR])
        self.progress = BooleanVar(self, value=REPARTY_CONFIG[KEYWORD_PROGRESS_BAR])

        # if there's a lot of settings, then add tabs
        # option_tabs = ttk.Notebook(self)
        # option_tabs.grid(row=0)

        Label(self, text="SpyParty Directory:").grid(row=0, column=0, sticky=EAST)
        Entry(self, textvariable=self.sp_dir, width=64).grid(row=0, column=1, columnspan=4)
        Button(self, text="Locate", width=6, command=self.locate_replays_directory).grid(
            row=0, column=5, padx=4, pady=3)

        Label(self, text="Show Progress Bar?").grid(row=1, column=0, sticky=EAST)
        Checkbutton(self, text="", variable=self.progress).grid(row=1, column=1, sticky=WEST)

        Button(self, text=" Save ", width=6, command=self._exit).grid(row=10, column=5, padx=4, pady=3)
        Button(self, text="Cancel", width=6, command=self.destroy).grid(row=10, column=6, sticky=WEST, padx=3, pady=3)

    def locate_replays_directory(self):
        if (path := filedialog.askdirectory(
                initialdir=REPARTY_CONFIG[KEYWORD_GAME_DIR],
                title="Select your SpyParty directory")):
            # todo make sure a SpyParty.prop is in this directory, simple validation
            self.sp_dir.set(path)
            self.tkraise()

    def _exit(self):
        REPARTY_CONFIG[KEYWORD_GAME_DIR] = self.sp_dir.get()
        REPARTY_CONFIG[KEYWORD_PROGRESS_BAR] = self.progress.get()
        REPARTY_CONFIG.save()
        self.destroy()


if __name__ == '__main__':
    SettingsModal().mainloop()
