from Filepaths import VENUE_IMAGES


class Venue:
    def __init__(self, name):
        self.name = name
        self.selected = True

    def get_image_path(self):
        return VENUE_IMAGES / f"{self.name.lower().replace(' ', '_')}.png"


class LegacyVenue(Venue):
    def __init__(self, name, prop_allowed=True):
        Venue.__init__(self, name)


venue_list = (  # flag for prop-able when I integrate quickplay generation (RIP moderns)
    Venue("Aquarium"),
    Venue("Balcony"),   LegacyVenue("Old Balcony"),
    Venue("Ballroom"),  LegacyVenue("Old Ballroom"),
    Venue("Courtyard"), LegacyVenue("Old Courtyard"),   LegacyVenue("Old Courtyard 2"),
    Venue("Gallery"),   LegacyVenue("Old Gallery"),
    Venue("High-rise"), LegacyVenue("Old High-rise", False),
    Venue("Library"),   LegacyVenue("Panopticon"),
    Venue("Moderne"),   LegacyVenue("Modern", False),   LegacyVenue("Double Modern", False),
    Venue("Pub"),
    Venue("Redwoods"),
    Venue("Teien"),
    Venue("Terrace"),   LegacyVenue("Old Terrace", False),
    Venue("Veranda"),   LegacyVenue("Old Veranda"),
)


class Mission:
    def __init__(self, mission_name):
        self.mission = mission_name
        self.shortened, *_ = mission_name.split(' ')

    def __str__(self):
        return self.mission


class HardTell(Mission):
    def __init__(self, mission_name):
        Mission.__init__(self, mission_name)


class SoftTell(Mission):
    def __init__(self, mission_name):
        Mission.__init__(self, mission_name)


mission_list = (
    HardTell('Bug Ambassador'),
    SoftTell('Contact Double Agent'),
    HardTell('Transfer Microfilm'),
    HardTell('Swap Statue'),
    SoftTell('Inspect Statues'),
    SoftTell('Seduce Target'),
    HardTell('Purloin Guest List'),
    SoftTell('Fingerprint Ambassador')
)

game_result_list = ('Missions Win', 'Time Out', 'Spy Shot', 'Civilian Shot')
# I sorted this in order in which you might want to replay snipe them
