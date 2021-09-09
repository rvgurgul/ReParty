from pathlib import Path
from Config import Config
from os import listdir

CWD = Path(__file__).parent

ASSETS = CWD / 'assets'
VENUE_IMAGES = ASSETS / 'venues'
ROLE_IMAGES = ASSETS / 'roles'

KEYWORD_GAME_DIR = 'SpyParty_directory'
KEYWORD_PROGRESS_BAR = 'show_progress_bar'
KEYWORD_QUERIED_SETS_DIR = 'queried_sets_folder'
KEYWORD_QUERIED_SETS_DATA = 'queried_sets_data'

# CWD / allows access to the config from project subdirectories
__REPARTY_CONFIG_FILE = CWD / 'ReParty_config.json'
REPARTY_CONFIG = Config(__REPARTY_CONFIG_FILE, default_config=lambda: {
    KEYWORD_GAME_DIR: rf'{Path.home()}\AppData\Local\SpyParty',
    KEYWORD_PROGRESS_BAR: 1,
    KEYWORD_QUERIED_SETS_DIR: 'ReParty Queried Sets',
    # KEYWORD_QUERIED_SETS_DATA: {}
}, load_logging=True)


def SPYPARTY_DIRECTORY():
    return Path(REPARTY_CONFIG[KEYWORD_GAME_DIR])


def QUICKPLAYS_DIRECTORY():
    return SPYPARTY_DIRECTORY() / 'quickplays'


def REPLAYS_DIRECTORY():
    return SPYPARTY_DIRECTORY() / 'replays'


def get_queried_sets_directory():
    return REPLAYS_DIRECTORY() / REPARTY_CONFIG[KEYWORD_QUERIED_SETS_DIR]


def get_current_queried_sets():
    qs_dir = get_queried_sets_directory()
    for queried_set in listdir(qs_dir):
        yield queried_set

