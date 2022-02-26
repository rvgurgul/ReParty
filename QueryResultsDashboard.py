from collections import Counter
from tkinter import Tk, Label, Button, Frame, ttk, Canvas, Menu
# from Filepaths import ROLE_IMAGES
# from PIL import Image, ImageTk

from QueriedSetsManager import QueriedSetModal
from SettingsModal import SettingsModal


class WinRecord:
    def __init__(self, wins=0, total=0):
        self.num = wins
        self.den = total

    def __str__(self):
        return f'{self.num}/{self.den}'

    def win(self):
        self.num += 1
        self.den += 1

    def loss(self):
        self.den += 1

    def __add__(self, other):
        return WinRecord(self.num + other.num, self.den + other.den) if isinstance(other, WinRecord) else self

    def percentage_string(self):
        return f'{round(100 * self.num / self.den, 1)}%' if self.den else 'UNDEFINED'


class QueryResultsDashboard(Tk):
    def __init__(self, replays):
        Tk.__init__(self)
        self.title('ReParty: Analysis Dashboard')
        self.replays = replays
        # could TECHNICALLY filter these replays further and open another AnalysisDashboard!
        self.geometry("+0+0")

        toolbar = Menu(self)
        self.config(menu=toolbar)
        menu_file = Menu(toolbar, tearoff=0)
        # todo prevent opening more than 1 modal at a time
        menu_file.add_command(label="Export to Replay Set", command=lambda: QueriedSetModal(self.replays).mainloop())
        menu_file.add_command(label="Settings", command=lambda: SettingsModal().mainloop())
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.destroy)
        toolbar.add_cascade(label="Menu", menu=menu_file)

        ROLE_SNIPER = 1
        ROLE_SPY = 2
        ROLE_STRS = {ROLE_SPY: 'Spy', ROLE_SNIPER: 'Sniper'}
        # ROLE_FILENAMES = {ROLE_SPY: 'spy.png', ROLE_SNIPER: 'sniper.png'}
        # __loaded_images = {}

        self.record = {}
        self.players = Counter()
        self.venues = Counter()  # could pass venue selection through to avoid recollection
        player_played_role = set()
        for replay in self.replays:
            self.players[replay.sniper] += 1
            self.players[replay.spy] += 1
            self.venues[replay.venue] += 1
            player_played_role.add((replay.sniper, ROLE_SNIPER))
            player_played_role.add((replay.spy, ROLE_SPY))
            if replay.sniper_win():
                self.record.setdefault((replay.venue, replay.sniper, ROLE_SNIPER), WinRecord()).win()
                self.record.setdefault((replay.venue, replay.spy, ROLE_SPY), WinRecord()).loss()
            elif replay.spy_win():
                self.record.setdefault((replay.venue, replay.sniper, ROLE_SNIPER), WinRecord()).loss()
                self.record.setdefault((replay.venue, replay.spy, ROLE_SPY), WinRecord()).win()

        container = ttk.Frame(self)
        canvas = Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        header = Frame(container)
        header.pack(side='top')
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        container.pack()

        COL_WIDTH_PLAYERS = 16
        COL_WIDTH_ROLES = 6
        COL_WIDTH_RESULTS = 9

        Label(header, text='Player', width=COL_WIDTH_PLAYERS).grid(row=0, column=0)
        Label(header, text='Role', width=COL_WIDTH_ROLES).grid(row=0, column=1)
        ordered_venues = [v for v, _ in self.venues.most_common()]
        venue_paddings = [COL_WIDTH_RESULTS + (len(v) - COL_WIDTH_RESULTS) // 2 for v in ordered_venues]

        def hover_label(event):
            label = event.widget
            if record := labels[label]:
                label['text'] = record.percentage_string()
                label['bg'] = '#42b3f5'

        def unhover_label(event):
            label = event.widget
            record = labels[label]
            label['text'] = record
            label['bg'] = 'SystemButtonFace'

        COL_OFFSET = 3
        # this approach avoids checking against this boolean P*V*2 times during the loops
        if len(ordered_venues) > 1:
            Label(header, text='Overall', width=COL_WIDTH_RESULTS).grid(row=0, column=2)
            COL_OFFSET += 1

            def add_row(player_, role_):
                cumulative = WinRecord()
                for index, venue_ in enumerate(ordered_venues):
                    venue_wl = self.record.get((venue_, player_, role_))
                    venue_label = Label(scrollable_frame, text=venue_wl, width=venue_paddings[index])
                    labels[venue_label] = venue_wl
                    venue_label.grid(row=row_num, column=index + COL_OFFSET)
                    cumulative += venue_wl
                cumulative_label = Label(scrollable_frame, text=cumulative, width=COL_WIDTH_RESULTS)
                labels[cumulative_label] = cumulative
                cumulative_label.grid(row=row_num, column=2)
        else:  # however, it does lead to some repetitious code
            def add_row(player_, role_):
                for index, venue_ in enumerate(ordered_venues):
                    venue_wl = self.record.get((venue_, player_, role_))
                    venue_label = Label(scrollable_frame, text=venue_wl, width=venue_paddings[index])
                    labels[venue_label] = venue_wl
                    venue_label.grid(row=row_num, column=index + COL_OFFSET)

        for i, venue in enumerate(ordered_venues):
            Label(header, text=venue, width=venue_paddings[i]).grid(row=0, column=i + COL_OFFSET)

        labels = {}
        row_num = 1
        for player, _ in self.players.most_common(40):  # todo too many results causes severe lag...
            roles_played = 0
            for ROLE in (role for role in (ROLE_SPY, ROLE_SNIPER) if (player, role) in player_played_role):
                roles_played += 1
                # img = Image.open(ROLE_IMAGES / ROLE_FILENAMES[ROLE]).resize((23, 27), Image.ANTIALIAS)
                # phim = ImageTk.PhotoImage(img)
                role_label = Label(scrollable_frame, text=ROLE_STRS[ROLE], width=COL_WIDTH_ROLES)
                # role_label.image = phim
                role_label.grid(row=row_num, column=1)
                add_row(player, ROLE)
                row_num += 1
            Label(scrollable_frame, text=player, width=COL_WIDTH_PLAYERS
                  ).grid(row=row_num - roles_played, column=0, rowspan=roles_played)

        for record_label in labels:
            record_label.bind('<Enter>', hover_label)
            record_label.bind('<Leave>', unhover_label)
