from tkinter import Tk
from Filepaths import get_queried_sets_directory
from shutil import copy


class RePartyQueriedSetsManager(Tk):
    def __init__(self, replays: list = None):
        Tk.__init__(self)
        self.title('ReParty: Queried Set Manager')
        self.protocol('WM_DELETE_WINDOW', self.destroy)

        if replays:
            # UI for adding replay set
            self.create_replay_sniper_set(replays)
        # UI for existing replay sets
        # - ABCD (17 games) [-]
        # - EFGH (32 games) [-]

    @staticmethod
    def create_replay_sniper_set(replays):
        # create a folder containing the queried games, which could be used as a replay sniper set
        qsd = get_queried_sets_directory()
        if not qsd.exists():  # create the folder, if it doesn't already exist
            qsd.mkdir()

        set_name = input('What would you like to call this replay set?\n')
        set_path = qsd / set_name
        print(set_path)
        if set_path.exists():
            print('This folder already exists. Cancel? Add? Replace?')
        else:
            set_path.mkdir()
            for replay in replays:
                # todo memory saving: move the replays, remember where they came from, then move them back?
                copy(replay.filepath, set_path)


if __name__ == '__main__':
    RePartyQueriedSetsManager([]).mainloop()
