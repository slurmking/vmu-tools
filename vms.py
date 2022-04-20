"""Reads and creates vms files"""
import os
import unicodedata
import image_gen



def filter_non_printable(text):
    """Filters text to printable ascii"""
    return ''.join(c for c in text if not unicodedata.category(c).startswith('C'))


class Vms:
    """Get data from VMS file"""

    def binary_read(self, offset, length):
        """reads binary from given offset"""
        self.vms.seek(int(offset, 16))
        return self.vms.read(length)

    def validate(self):
        """checks if VMS file is valid"""
        if self.icon_count > 3:
            self.invalid = True
        elif self.animation_speed > 65535:
            self.invalid = True

    def text_read(self, text):
        """Decodes binary to cp932 text"""
        text = text.decode('cp932', errors='replace')
        text = filter_non_printable(text)
        return text

    def gamesave_read(self):
        """Reads gamesave type info"""
        self.description = self.text_read(self.binary_read("10", 32))
        self.creating_app = self.text_read(self.binary_read("30", 16))
        self.icon_count = int.from_bytes(self.binary_read("40", 2), "little")
        self.animation_speed = int.from_bytes(self.binary_read("42", 2), "little")
        self.eyecatch_type = int.from_bytes(self.binary_read("44", 2), "little")
        self.crc = int.from_bytes(self.binary_read("46", 2), "little")
        self.data_size = int.from_bytes(self.binary_read("48", 4), "little")
        self.icon_palette = self.binary_read("60", 32)
        self.icon_bitmaps = self.binary_read("80", 512 * self.icon_count)

    def icondata_read(self):
        """Reads icondata type info"""
        self.mono_offset = hex(int.from_bytes(self.binary_read("10", 4), "little"))
        self.icon_offset = int.from_bytes(self.binary_read("14", 4), "little")
        self.title = self.binary_read("00", 16)
        self.mono_bitmap = self.binary_read(self.mono_offset, 128)
        self.icon_palette = self.binary_read(hex(self.icon_offset), 32)
        self.icon_bitmaps = self.binary_read(hex(self.icon_offset + 32), 512)
        self.icon_count = 1
        self.animation_speed = 1
        self.description = "ICONDATA"

    def game_read(self):
        """reads game type info"""
        self.title = self.text_read(self.binary_read("200", 16))
        self.description = self.text_read(self.binary_read("210", 32))
        self.icon_count = int.from_bytes(self.binary_read("240", 2), "little")
        self.animation_speed = int.from_bytes(self.binary_read("242", 2), "little")
        self.data_size = int.from_bytes(self.binary_read("48", 4), "little")
        self.icon_palette = self.binary_read("260", 32)
        self.icon_bitmaps = self.binary_read("280", 512 * self.icon_count)

    def icon_gen(self):
        """Generates icon and saves image"""
        save = self.description
        if self.filetype == 2:
            save = self.title
        image_gen.animated_gen(self.icon_bitmaps, self.icon_palette, self.icon_count, save, self.animation_speed)
        if self.filetype == 1:
            # Keeps leading zeros from monoBitmap bytes
            image_gen.bnw_gen((bin(int('1' + self.mono_bitmap.hex(), 16))[3:]), save)

    def info(self):
        """Generates Info Dictionary"""
        info = {"title": self.title,
                "description": self.description,
                "creatingApp": self.creating_app,
                "IconCount": self.icon_count,
                "Animation Speed": self.animation_speed,
                "CRC": self.crc,
                "Data Size": self.data_size,
                "Type": self.filetype,
                "invalid": self.invalid,
                "fileSize": self.vms_file_size,
                "vmsName": self.vms_name}
        return info

    def image_data(self):
        """Grabs icon data"""
        image = {"iconBitmap": self.icon_bitmaps,
                     "iconPalette": self.icon_palette,
                     "IconCount": self.icon_count, }
        if self.filetype == 1:
            # Keeps leading zeros from monoBitmap bytes
            image["monoBitmap"] = (bin(int('1' + self.mono_bitmap.hex(), 16))[3:])
        return image

    def __init__(self, file):
        self.vms = open(file, 'rb')
        self.title = ''
        self.description = ''
        self.creating_app = ''
        self.icon_count = 0
        self.animation_speed = 0
        self.eyecatch_type = 0
        self.crc = 0
        self.data_size = 0
        self.icon_palette = []
        self.icon_bitmaps = 0
        self.invalid = False
        self.vms_file_size = os.path.getsize(file)
        self.vms_name = os.path.basename(self.vms.name)

        # Check filetype
        # gamesave = 0 ICONDATA = 1 Game = 2'''
        # only way I could check not sure if there is a better method'
        if self.binary_read("E0", 16).hex() == "00000000000000000000000000000000" or self.binary_read("E0",
                                                                                                      16).hex() == "ffffffffffffffffffffffffffffffff":
            self.filetype = 2
            self.game_read()
            self.validate()
        elif "ICONDATA.VMS" in file:
            self.filetype = 1
            self.icondata_read()
            self.validate()
        else:
            self.filetype = 0
            self.gamesave_read()
            self.validate()
