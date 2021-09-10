from tkinter import Tk, Label, Entry, Button, Checkbutton, IntVar
from Filepaths import get_queried_sets_directory
from shutil import copy
from Helpers import windows_filename_sanitizer


class QueriedSetModal(Tk):
    def __init__(self, replays):
        Tk.__init__(self)

        self.replays = replays
        self.memory_saver = IntVar()

        Label(self, text='What would you like to call this replay set?').grid(row=1, columnspan=4)
        self.text_entry = Entry(self, width=40)
        self.text_entry.grid(row=2, columnspan=4, padx=6, pady=6)
        # todo sanitize in real time

        Button(self, text='Cancel', command=self.destroy, width=10).grid(row=4, column=0)
        Checkbutton(self, text='Memory-saver mode?\n(Coming soon™)', variable=self.memory_saver, width=20).grid(
            row=4, column=1, columnspan=2)
        self.action_button = Button(self, text='Create', command=self.create_replay_sniper_set, width=10)
        self.action_button.grid(row=4, column=3)
        self.create_mode = True

    def text_updated(self, *_):
        self.text_entry['text'] = windows_filename_sanitizer(self.text_entry.get())
        print(self.text_entry.get())
        if not self.create_mode:
            self.create_mode = True
            self.action_button['text'] = 'Create'
            self.action_button['command'] = self.create_replay_sniper_set

    def create_replay_sniper_set(self):
        """Creates a folder containing the queried games, which can be used as a replay sniper set."""
        if set_name := windows_filename_sanitizer(self.text_entry.get()):
            set_path = get_queried_sets_directory() / set_name
            print(set_path)
            if set_path.exists():
                Label(self, text='A set already exists under this name!').grid(row=3, columnspan=4)
                self.action_button['text'] = 'Add Anyway?'
                self.action_button['command'] = lambda: self.confirm_set(set_path)
                self.create_mode = False
            else:
                set_path.mkdir()
                self.confirm_set(set_path)

    def confirm_set(self, directory):
        self.__copy_replays_to_directory(directory)
        # if self.memory_saver.get():
        #     self.__move_replays_to_directory(directory)
        # else:
        #     self.__copy_replays_to_directory(directory)
        self.action_button['text'] = 'Success!'
        self.action_button['command'] = self.destroy

    def __move_replays_to_directory(self, directory):
        # todo memory saving: move the replays, remember where they came from, then move them back?
        pass

    def __copy_replays_to_directory(self, directory):
        for replay in self.replays:
            copy(replay.filepath, directory)

    # I am very wary of attempting to delete files. I would hate to make a mistake.
    # def __replace_replays_in_directory(self, directory):
    #     pass

# class QueriedSetsManager(Tk):
#     def __init__(self):
#         Tk.__init__(self)
#         self.title('ReParty: Queried Set Manager')
#         self.protocol('WM_DELETE_WINDOW', self.destroy)
#
#         # UI for existing replay sets
#         # - ABCD (17 games) [-]
#         # - EFGH (32 games) [-]


if __name__ == '__main__':
    # QueriedSetsManager().mainloop()
    QueriedSetModal([]).mainloop()
