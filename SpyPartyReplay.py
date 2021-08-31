from base64 import urlsafe_b64encode
from datetime import datetime
from struct import unpack


class SpyPartyReplay:  # todo replace usage of ReplayParser
    class ParsingException(Exception):
        pass

    class Player:
        def __init__(self, username, display_name):
            self.username = username
            self.steam = display_name.endswith('/steam')
            self.display_name = display_name[:-6] if self.steam else display_name

        def __str__(self):
            return self.display_name

    class __ReplayVersionConstants:
        def __init__(
                self, magic_number=0x00, file_version=0x04, protocol_version=0x08, spyparty_version=0x0C,
                duration=0x14, uuid=0x18, timestamp=0x28, playid=0x2C, players=0x50,
                len_user_spy=0x2E, len_user_sniper=0x2F, len_disp_spy=None, len_disp_sniper=None,
                guests=None, clock=None, result=0x30, setup=0x34, venue=0x38, variant=None,
                missions_s=0x3C, missions_p=0x40, missions_c=0x44
        ):
            self.magic_number = magic_number
            self.file_version = file_version
            self.protocol_version = protocol_version
            self.spyparty_version = spyparty_version
            self.duration = duration
            self.uuid = uuid
            self.timestamp = timestamp
            self.playid = playid
            self.players = players
            self.len_user_spy = len_user_spy
            self.len_user_sniper = len_user_sniper
            self.len_disp_spy = len_disp_spy
            self.len_disp_sniper = len_disp_sniper
            self.guests = guests
            self.clock = clock
            self.result = result
            self.setup = setup
            self.venue = venue
            self.variant = variant
            self.missions_s = missions_s
            self.missions_p = missions_p
            self.missions_c = missions_c

        @staticmethod
        def read_bytes(sector, start, length):
            return sector[start:(start + length)]

        def extract_names(self, sector):
            total_offset = self.players

            spy_user_len = sector[self.len_user_spy]
            spy_username = self.read_bytes(sector, total_offset, spy_user_len).decode()
            total_offset += spy_user_len

            sni_user_len = sector[self.len_user_sniper]
            sniper_username = self.read_bytes(sector, total_offset, sni_user_len).decode()

            spy_display_name, sniper_display_name = spy_username, sniper_username
            if self.len_disp_spy or self.len_disp_sniper:
                total_offset += sni_user_len
                spy_disp_len = sector[self.len_disp_spy]
                spy_display_name = self.read_bytes(sector, total_offset, spy_disp_len).decode()

                total_offset += spy_disp_len
                sni_disp_len = sector[self.len_disp_sniper]
                sniper_display_name = self.read_bytes(sector, total_offset, sni_disp_len).decode()

                if not spy_display_name:
                    spy_display_name = spy_username
                if not sniper_display_name:
                    sniper_display_name = sniper_username
            return spy_display_name, sniper_display_name, spy_username, sniper_username

    __HEADER_DATA_MINIMUM_BYTES = 416
    __HEADER_DATA_USERNAME_LIMIT = 33
    __HEADER_DATA_DISPLAYNAME_LIMIT = 135
    __HEADER_DATA_MAXIMUM_BYTES = __HEADER_DATA_MINIMUM_BYTES + 2 * (__HEADER_DATA_USERNAME_LIMIT +
                                                                     __HEADER_DATA_DISPLAYNAME_LIMIT)
    __OFFSETS_DICT = {
        3: __ReplayVersionConstants(),
        4: __ReplayVersionConstants(
            players=0x54,
            result=0x34,
            setup=0x38,
            venue=0x3C,
            missions_s=0x40,
            missions_p=0x44,
            missions_c=0x48
        ),
        5: __ReplayVersionConstants(
            players=0x60,
            len_user_spy=0x2E,
            len_user_sniper=0x2F,
            len_disp_spy=0x30,
            len_disp_sniper=0x31,
            guests=0x50,
            clock=0x54,
            result=0x38,
            setup=0x3C,
            venue=0x40,
            missions_s=0x44,
            missions_p=0x48,
            missions_c=0x4C
        ),
        6: __ReplayVersionConstants(
            players=0x64,
            len_user_spy=0x2E,
            len_user_sniper=0x2F,
            len_disp_spy=0x30,
            len_disp_sniper=0x31,
            guests=0x54,
            clock=0x58,
            result=0x38,
            setup=0x3C,
            venue=0x40,
            variant=0x44,
            missions_s=0x48,
            missions_p=0x4C,
            missions_c=0x50
        )
    }

    __VENUE_MAP = {
        0x8802482A: "Old High-rise",
        0x3A30C326: "High-rise",
        0x5996FAAA: "Ballroom",
        0x5B121925: "Ballroom",
        0x1A56C5A1: "High-rise",
        0x28B3AA5E: "Old Gallery",
        0x290A0C75: "Old Courtyard 2",
        0x3695F583: "Panopticon",
        0xA8BEA091: "Old Veranda",
        0xB8891FBC: "Old Balcony",
        0x0D027340: "Pub",  # I slapped a 0 on the front, assuming that's the only way it outputted 7 hex digits
        0x3B85FFF3: "Pub",
        0x09C2E7B0: "Old Ballroom",  # this one too
        0xB4CF686B: "Old Courtyard",
        0x7076E38F: "Double Modern",
        0xE6146120: "Modern",
        0x6F81A558: "Veranda",
        0x9DC5BB5E: "Courtyard",
        0x168F4F62: "Library",
        0x1DBD8E41: "Balcony",
        0x7173B8BF: "Gallery",
        0x9032CE22: "Terrace",
        0x2E37F15B: "Moderne",
        0x79DFA0CF: "Teien",
        0x98E45D99: "Aquarium",
        0x35AC5135: "Redwoods",
        0xF3E61461: "Modern",
    }
    __VARIANT_MAP = {
        "Teien": [
            "BooksBooksBooks",
            "BooksStatuesBooks",
            "StatuesBooksBooks",
            "StatuesStatuesBooks",
            "BooksBooksStatues",
            "BooksStatuesStatues",
            "StatuesBooksStatues",
            "StatuesStatuesStatues"
        ],
        "Aquarium": [
            "Bottom",
            "Top"
        ],
    }
    __RESULT_MAP = {
        0: "Missions Win",
        1: "Time Out",
        2: "Spy Shot",
        3: "Civilian Shot",
        4: "In Progress"
    }
    __MODE_MAP = {
        0: "k",
        1: "p",
        2: "a"
    }
    __MISSION_OFFSETS = {
        "Bug": 0,
        "Contact": 1,
        "Transfer": 2,
        "Swap": 3,
        "Inspect": 4,
        "Seduce": 5,
        "Purloin": 6,
        "Fingerprint": 7,
    }

    def __unpack_missions(self, sector, offset, container_type):
        data = self.__unpack_int(sector, offset)
        missions = container_type()
        if container_type == set:
            for mission in self.__MISSION_OFFSETS:
                if data & (1 << self.__MISSION_OFFSETS[mission]):
                    missions.add(mission)
        elif container_type == list:
            for mission in self.__MISSION_OFFSETS:
                if data & (1 << self.__MISSION_OFFSETS[mission]):
                    missions.append(mission)
        return missions

    @staticmethod
    def __read_bytes(sector, start, length):
        return sector[start:(start + length)]

    @staticmethod
    def __unpack_byte(sector, offset):
        return unpack('B', sector[offset])[0]

    def __unpack_float(self, sector, offset):
        return unpack('f', self.__read_bytes(sector, offset, 4))[0]

    def __unpack_int(self, sector, start):
        return unpack('I', self.__read_bytes(sector, start, 4))[0]

    def __unpack_short(self, sector, start):
        return unpack('H', self.__read_bytes(sector, start, 2))[0]

    def __init__(self, filepath, mission_container=set):
        with open(filepath, "rb") as replay_file:
            bytes_read = bytearray(replay_file.read(self.__HEADER_DATA_MAXIMUM_BYTES))

            if len(bytes_read) < self.__HEADER_DATA_MINIMUM_BYTES:
                raise SpyPartyReplay.ParsingException(
                    f"A minimum of {self.__HEADER_DATA_MINIMUM_BYTES} bytes are required to parse: {filepath}")
            if bytes_read[:4] != b"RPLY":
                raise SpyPartyReplay.ParsingException(f"Unknown File ({filepath})")

            replay_version = self.__unpack_int(bytes_read, 0x04)
            try:
                offsets = self.__OFFSETS_DICT[replay_version]
            except KeyError:
                raise SpyPartyReplay.ParsingException(f"Unknown file version: {replay_version} ({filepath})")

            # passed all possible exceptions, start assigning values
            self.filepath = filepath
            self.date = datetime.fromtimestamp(self.__unpack_int(bytes_read, offsets.timestamp))

            self.venue = self.__VENUE_MAP[self.__unpack_int(bytes_read, offsets.venue)]
            if self.venue == 'Terrace' and self.__unpack_int(bytes_read, offsets.spyparty_version) < 6016:
                self.venue = 'Old Terrace'
            self.variant = None
            if offsets.variant:
                try:
                    self.variant = self.__VARIANT_MAP[self.venue][self.__unpack_int(bytes_read, offsets.variant)]
                except KeyError as e:
                    print(e)

            uuid_offset = offsets.uuid
            self.uuid = urlsafe_b64encode(bytes_read[uuid_offset:uuid_offset + 16]).decode()
            self.playid = self.__unpack_short(bytes_read, offsets.playid)
            name_extracts = offsets.extract_names(bytes_read)
            self.spy = SpyPartyReplay.Player(name_extracts[0], name_extracts[2])
            self.sniper = SpyPartyReplay.Player(name_extracts[1], name_extracts[3])
            self._result = self.__unpack_int(bytes_read, offsets.result)

            setup_info = self.__unpack_int(bytes_read, offsets.setup)
            self._game_type = setup_info >> 28
            self.missions_available = (setup_info & 0x0FFFC000) >> 14
            self.missions_required = setup_info & 0x00003FFF

            self.guests = self.__unpack_int(bytes_read, offsets.guests) if offsets.guests else None
            self.start_clock = self.__unpack_int(bytes_read, offsets.clock) if offsets.clock else None
            self.duration = int(self.__unpack_float(bytes_read, offsets.duration))
            self.selected_missions = self.__unpack_missions(bytes_read, offsets.missions_s, mission_container)
            self.picked_missions = self.__unpack_missions(bytes_read, offsets.missions_p, mission_container)
            self.completed_missions = self.__unpack_missions(bytes_read, offsets.missions_c, mission_container)

    def get_game_result(self):
        return SpyPartyReplay.__RESULT_MAP[self._result]

    def get_game_type(self):
        return SpyPartyReplay.__MODE_MAP[self._game_type]


