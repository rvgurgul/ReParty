from tkinter import Tk, Label, Button, TOP, X as FILLX


class Cleaner:
    def __init__(self, clean_func):
        self.cleaned = {}  # remember how different strings were cleaned
        self.func = clean_func

    def clean(self, text):
        return self.cleaned.setdefault(text, self.func(text))


def font_verdana(size):
    return 'Verdana', size


def dialog_modal(title, prompt):
    popup = Tk()
    popup.wm_title(title)
    Label(popup, text=prompt, font=font_verdana(11)).pack(side=TOP, fill=FILLX, pady=10)
    Button(popup, text="OK", command=popup.destroy).pack()
    popup.mainloop()


def lister(items):
    count = len(items)
    return (
        '' if count == 0 else
        str(items[0]) if count == 1 else  # could fail on an unordered type, like set
        ' & '.join(items) if count == 2 else
        ', '.join(items[:-1]) + ' & ' + str(items[-1])
    )


def windows_filename_sanitizer(entered_string, to_char='_'):
    for char in '\\/:*?"<>|':  # one stackoverflow post claimed chained .replace() calls is the fastest approach
        entered_string = entered_string.replace(char, to_char)
    return entered_string

    # class GameType:
    #     class InvalidGameTypeException(Exception):
    #         pass
    #
    #     ANY = 'Any'
    #     PICK = 'Pick'
    #     KNOWN = 'Known'
    #
    # class Setup:
    #     def __init__(self, game_type, required, available):
    #         if not isinstance(game_type, SpyPartyReplay.GameType):  # i don't think this is gonna work right
    #             raise SpyPartyReplay.GameType.InvalidGameTypeException(f'"{game_type}" is not a valid game type.')
    #         self.game_type = game_type
    #         self.required = required
    #         self.availabe = available
    #
    #     def __str__(self):
    #         if self.game_type is SpyPartyReplay.GameType.KNOWN:
    #             return f'{self.game_type} {self.required}'
    #         elif self.game_type is SpyPartyReplay.GameType.ANY or self.game_type is SpyPartyReplay.GameType.PICK:
    #             return f'{self.game_type} {self.required}/{self.availabe}'

